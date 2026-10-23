#!/usr/bin/env python3
"""Shelly adapter: makes each Shelly Gen2/Gen3 relay look like a light per Lights-MQTT-Contract v1.2.

Shelly side (MQTT prefix set on the device, e.g. shelly/front_door_flood):
  <prefix>/online           true/false, retained (the Shelly's own last will)
  <prefix>/status/switch:0  full switch status on every change
  <prefix>/events/rpc       NotifyStatus deltas (used for watts updates)
  <prefix>/rpc              we send Switch.Set / Switch.GetStatus here; replies come back on <src>/rpc
Contract side: dashboard/lights/<id>/{set,state,availability,config}

One MQTT connection per light, each with its own last will (offline on that light's availability),
so if this adapter dies, every light it serves shows offline on the dashboard within seconds.
"""
import json, signal, threading, time
import paho.mqtt.client as mqtt

# Light ID -> its Shelly's MQTT prefix and how the dashboard shows it. IDs and group_ids never change.
DEVICES = {
    'side_deck_flood': {'shelly': 'shelly/side_deck_flood', 'name': 'Side Deck',
                        'group': 'Outdoor Flood Lights', 'group_id': 'outdoor_flood_lights'},
    'front_door_flood': {'shelly': 'shelly/front_door_flood', 'name': 'Front Door',
                         'group': 'Outdoor Flood Lights', 'group_id': 'outdoor_flood_lights'},
}
HOST, PORT = '127.0.0.1', 1883   # services on the Pi use 1883; the Shellys themselves use 1884
WATTS_STEP = 2.0                 # republish state when watts move this much
DEAD_W = 5.0                     # crossing this always republishes (the dead-fixture check uses it)
REFRESH_S = 300                  # backstop: ask each online Shelly for fresh status this often
CAUSE = {'switch': 'switch', 'button': 'switch', 'init': 'boot',
         'timer': 'schedule', 'loopback': 'schedule', 'schedule': 'schedule'}   # anything else: command

def log(s): print(time.strftime('%Y-%m-%d %H:%M:%S'), s, flush=True)

class Light:
    def __init__(self, lid, d):
        self.id, self.d, self.pre = lid, d, d['shelly']
        self.T = f'dashboard/lights/{lid}/'
        self.src = f'shelly-adapter/{lid}'
        self.lock = threading.Lock()
        self.online = None          # the Shelly's own online flag; None = not heard yet
        self.sw = {}                # cached switch:0 status
        self.last = None            # last published (state, watts)
        self.cause = 'boot'
        self.boot = False           # first state after the Shelly comes online is cause "boot"
        self.force = False          # publish the next status even if unchanged (confirms a set)
        self.rid = 0
        try: c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f'shelly-adapter-{lid}')
        except AttributeError: c = mqtt.Client(client_id=f'shelly-adapter-{lid}')
        c.will_set(self.T + 'availability', 'offline', qos=1, retain=True)
        c.reconnect_delay_set(1, 30)
        c.on_connect, c.on_message = self.on_connect, self.on_message
        self.c = c

    def start(self):
        self.c.connect_async(HOST, PORT, 15); self.c.loop_start()

    def stop(self):
        try: self.c.publish(self.T + 'availability', 'offline', qos=1, retain=True).wait_for_publish(3)
        except Exception: pass
        self.c.disconnect(); self.c.loop_stop()

    # ---- MQTT ----
    def on_connect(self, c, ud, flags, rc, *x):
        if rc != 0: log(f'{self.id}: broker refused the connection ({rc})'); return
        with self.lock: self.online, self.last = None, None
        cfg = {'v': 1, 'id': self.id, 'name': self.d['name'], 'group': self.d['group'],
               'group_id': self.d['group_id'], 'capabilities': ['onoff', 'power']}
        c.publish(self.T + 'config', json.dumps(cfg), qos=1, retain=True)
        c.subscribe([(self.pre + '/online', 1), (self.pre + '/status/switch:0', 1),
                     (self.pre + '/events/rpc', 1), (self.src + '/rpc', 1), (self.T + 'set', 1)])
        log(f'{self.id}: connected to the broker; listening for the Shelly on {self.pre}')

    def on_message(self, c, ud, m):            # one bad message must not kill the thread
        try: self.handle(m.topic, m.payload)
        except Exception as e: log(f'{self.id}: ignored bad message on {m.topic}: {e!r}')

    def handle(self, t, p):
        if t == self.pre + '/online':
            on = p.strip().lower() == b'true'
            with self.lock:
                if on == self.online: return
                self.online = on
                if on: self.boot, self.last = True, None
            self.c.publish(self.T + 'availability', 'online' if on else 'offline', qos=1, retain=True)
            log(f'{self.id}: Shelly {"ONLINE" if on else "OFFLINE"}')
            if on: self.rpc('Switch.GetStatus', {'id': 0})
        elif t == self.pre + '/status/switch:0':
            self.merge(json.loads(p))
        elif t == self.pre + '/events/rpc':
            s = json.loads(p)
            part = s.get('params', {}).get('switch:0') if s.get('method') == 'NotifyStatus' else None
            if isinstance(part, dict): self.merge(part)
        elif t == self.src + '/rpc':
            s = json.loads(p)
            if 'error' in s: log(f'{self.id}: Shelly RPC error {s["error"]}'); return
            r = s.get('result')
            if isinstance(r, dict) and 'output' in r: self.merge(r)      # a Switch.GetStatus reply
        elif t == self.T + 'set':
            self.command(json.loads(p))

    # ---- Shelly status -> contract state ----
    def merge(self, s):
        if not isinstance(s, dict): return
        with self.lock:
            self.sw.update(s)
            if not self.online or 'output' not in self.sw: return
            st = 'on' if self.sw['output'] else 'off'
            w = float(self.sw.get('apower') or 0.0) if st == 'on' else 0.0   # an open relay draws nothing
            prev = self.last
            flipped = prev is None or prev[0] != st
            crossed = prev is not None and (prev[1] < DEAD_W) != (w < DEAD_W)
            if not (flipped or crossed or self.force or abs(prev[1] - w) >= WATTS_STEP): return
            if self.boot: self.cause = 'boot'
            elif flipped and prev is not None: self.cause = CAUSE.get(self.sw.get('source'), 'command')
            elif self.force: self.cause = 'command'
            self.boot = self.force = False
            self.last = (st, w)
            msg = {'v': 1, 'state': st, 'watts': round(w, 1), 'cause': self.cause}
        self.c.publish(self.T + 'state', json.dumps(msg), qos=1, retain=True)
        if flipped or crossed: log(f"{self.id}: -> state {st} ({msg['cause']}, {msg['watts']} W)")
        if flipped and st == 'on':              # power reading lags the relay: fetch it again shortly
            threading.Timer(3, self.rpc, ('Switch.GetStatus', {'id': 0})).start()

    # ---- contract set -> Shelly ----
    def command(self, s):
        st = s.get('state') if isinstance(s, dict) else None
        if st not in ('on', 'off'): log(f'{self.id}: ignored set {s!r} (only on/off allowed)'); return
        with self.lock:
            if not self.online: log(f'{self.id}: set {st} while the Shelly is offline: not sent'); return
            self.force = True                   # the reply confirms it, even if it was already that way
        log(f"{self.id}: <- set {st} ({s.get('source')})")
        self.rpc('Switch.Set', {'id': 0, 'on': st == 'on'})
        self.rpc('Switch.GetStatus', {'id': 0})

    def rpc(self, method, params):
        with self.lock: self.rid += 1; rid = self.rid
        self.c.publish(self.pre + '/rpc', json.dumps(
            {'id': rid, 'src': self.src, 'method': method, 'params': params}), qos=1)

lights = [Light(i, d) for i, d in DEVICES.items()]
done = threading.Event()
signal.signal(signal.SIGTERM, lambda *a: done.set())
signal.signal(signal.SIGINT, lambda *a: done.set())
log(f'shelly-adapter starting: {", ".join(DEVICES)}')
for l in lights: l.start()
while not done.wait(REFRESH_S):
    for l in lights:
        if l.online: l.rpc('Switch.GetStatus', {'id': 0})
for l in lights: l.stop()
log('shelly-adapter stopped; its lights are marked offline')
