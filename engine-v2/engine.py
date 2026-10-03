#!/usr/bin/env python3
"""Automation engine v2, v0.1.1: clock windows for lights.
Talks only MQTT, per Lights-MQTT-Contract v1.1 (state is current only while online)."""
import json, os, time, logging, subprocess, threading
from datetime import datetime
import paho.mqtt.client as mqtt

HOME = os.path.expanduser('~/engine-v2')
RULES, STATE = f'{HOME}/rules.json', f'{HOME}/state.json'
DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
CONFIRM_S, RETRY_S, TICK_S, RECHECK_S = 5, 30, 5, 5
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m-%d %H:%M:%S', level=logging.INFO)
log = logging.info
dev, want, lock = {}, {}, threading.Lock()
# state.json = {rule_id: [targets]} for each rule active at the last tick
try: prev = json.load(open(STATE))
except Exception: prev = {}
if not isinstance(prev, dict) or not all(isinstance(v, list) for v in prev.values()):
    prev = {}                                          # old v0.1 format: start clean
FIRST, SAVED = [True], [json.dumps(prev, sort_keys=True)]
_clk = {'ok': False, 't': 0}

def clock_ok():
    if _clk['ok']: return True
    if time.time() - _clk['t'] < 60: return False
    _clk['t'] = time.time()
    r = subprocess.run(['timedatectl', 'show', '-p', 'NTPSynchronized', '--value'],
                       capture_output=True, text=True).stdout.strip()
    _clk['ok'] = (r == 'yes')
    log('clock synchronized: time rules enabled' if _clk['ok'] else 'clock NOT synchronized: holding time rules')
    return _clk['ok']

def hm(s):
    h, m = map(int, s.split(':')); return h * 60 + m

def active(r, now):
    days = r.get('days', DAYS); s, e = hm(r['start']['clock']), hm(r['end']['clock'])
    n, wd = now.hour * 60 + now.minute, now.weekday()
    if s <= e: return s <= n < e and DAYS[wd] in days
    if n >= s: return DAYS[wd] in days                # crosses midnight:
    return n < e and DAYS[(wd - 1) % 7] in days       # the day belongs to the start

def save_state():                                     # only on change; temp file + rename
    s = json.dumps(prev, sort_keys=True)
    if s == SAVED[0]: return
    with open(STATE + '.tmp', 'w') as f:
        f.write(s); f.flush(); os.fsync(f.fileno())
    os.replace(STATE + '.tmp', STATE); SAVED[0] = s

def set_want(i, state, why):
    want[i] = {'state': state, 'by': why, 'ok': False, 'sent': None, 'tries': 0,
               'warned': False, 'gave_up': False, 'manual': False, 'recheck': None}
    transmit(i)

def transmit(i):
    w = want[i]; w['recheck'] = None
    if not dev.get(i, {}).get('online'):
        w['sent'] = None
        log(f"{i}: want {w['state']} ({w['by']}) but light is offline; will send when it returns")
        return
    w['sent'], w['warned'] = time.time(), False
    w['tries'] += 1
    c.publish(f'dashboard/lights/{i}/set',
              json.dumps({'v': 1, 'state': w['state'], 'source': 'engine'}), qos=1)
    log(f"{i}: -> {w['state']} ({w['by']}), try {w['tries']}")

def on_message(cl, ud, m):                            # one bad message must not kill the thread
    try: handle(m)
    except Exception as e: log(f'ignored bad message on {m.topic}: {e!r}')

def handle(m):
    p = m.topic.split('/')
    if len(p) != 4: return
    i, kind = p[2], p[3]
    with lock:
        d = dev.setdefault(i, {'online': False, 'state': None, 'watts': 0.0})
        w = want.get(i)
        if kind == 'availability':
            on = m.payload.decode() == 'online'
            if on == d['online']: return
            log(f'{i}: ONLINE' if on else f'{i}: OFFLINE (state is now last-known only)')
            d['online'] = on
            if w and not w['manual']:                 # wait for its state before re-sending
                w.update(ok=False, sent=None, recheck=time.time() if on else None)
                if on: w.update(tries=0, gave_up=False)
        elif kind == 'state':
            s = json.loads(m.payload)
            if not isinstance(s, dict): raise ValueError('state is not a JSON object')
            st = s.get('state')
            d.update(state=st, watts=s.get('watts', 0.0))
            if not (w and d['online']): return
            if st == w['state']:
                if not w['ok']: log(f"{i}: confirmed {st} ({s.get('watts')} W)")
                w.update(ok=True, manual=False, recheck=None)
            elif w['ok']:
                w.update(ok=False, manual=True, sent=None)
                log(f"{i}: changed to {st} by {s.get('cause')}; leaving it until the next edge")
            elif w['recheck'] and not w['manual']:
                log(f'{i}: came back {st}, re-applying {w["state"]}'); transmit(i)

def end_targets(rid, tg, on_now, why):
    log(f'rule {rid}: END{why}')
    for i in tg:
        if i in on_now: log(f'{i}: stays on, another rule still wants it')
        else: set_want(i, 'off', rid)

def tick():
    if not clock_ok(): return
    try: rules = [r for r in json.load(open(RULES))['rules'] if r.get('enabled', True)]
    except Exception as e: log(f'rules.json unreadable: {e}'); return
    now, first = datetime.now(), FIRST[0]
    with lock:
        act = {r['id']: active(r, now) for r in rules}
        on_now = {i for r in rules if act[r['id']] for i in r['targets']}
        for rid in [k for k in prev if k not in act]:          # disabled or deleted mid-window
            end_targets(rid, prev.pop(rid), on_now, ' (disabled or removed)')
        for r in rules:
            rid, a, tg = r['id'], act[r['id']], list(r['targets'])
            if a and (rid not in prev or first):
                log(f'rule {rid}: START' + (' (catch-up at engine start)' if first else ''))
                for i in tg: set_want(i, 'on', rid)
            elif a and prev[rid] != tg:                         # targets edited mid-window
                end_targets(rid, [i for i in prev[rid] if i not in tg], on_now, ' for removed targets')
                for i in tg:
                    if i not in prev[rid]: set_want(i, 'on', rid)
            elif not a and rid in prev:
                end_targets(rid, prev.pop(rid), on_now, '')
            if a: prev[rid] = tg
        for i, w in want.items():
            if w['ok'] or w['manual']: continue
            if w['recheck'] and time.time() - w['recheck'] > RECHECK_S:
                log(f'{i}: back online but sent no state; re-sending'); transmit(i); continue
            if not w['sent']: continue
            age = time.time() - w['sent']
            if age > CONFIRM_S and not w['warned']:
                w['warned'] = True; log(f"{i}: NOT RESPONDING (no confirm of {w['state']} in {CONFIRM_S}s)")
            if age > RETRY_S:
                if w['tries'] < 2: transmit(i)
                elif not w['gave_up']: w['gave_up'] = True; log(f'{i}: giving up until it reconnects')
    FIRST[0] = False
    save_state()

try: c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='engine-v2')
except AttributeError: c = mqtt.Client(client_id='engine-v2')
c.on_connect = lambda cl, ud, fl, rc, *x: (log(f'broker connected (rc={rc})'),
    cl.subscribe([('dashboard/lights/+/state', 1), ('dashboard/lights/+/availability', 1)]))
c.on_message = on_message
c.connect_async('127.0.0.1', 1883, 30); c.loop_start()   # keeps retrying if the broker is down
log('engine-v2 v0.1.1 started'); time.sleep(2)
while True:
    try: tick()
    except Exception as e: log(f'tick failed: {e!r}')       # one bad rule must not kill the engine
    time.sleep(TICK_S)
