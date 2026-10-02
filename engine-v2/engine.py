#!/usr/bin/env python3
"""Automation engine v2, v0.1: clock windows for lights.
Talks only MQTT, per Lights-MQTT-Contract v1.1 (state is current only while online)."""
import json, os, time, logging, subprocess, threading
from datetime import datetime
import paho.mqtt.client as mqtt

HOME = os.path.expanduser('~/engine-v2')
RULES, STATE = f'{HOME}/rules.json', f'{HOME}/state.json'
DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
CONFIRM_S, RETRY_S, TICK_S = 5, 30, 5
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m-%d %H:%M:%S', level=logging.INFO)
log = logging.info
dev, want, lock = {}, {}, threading.Lock()
try: prev = json.load(open(STATE))
except Exception: prev = {}
FIRST = [True]
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

def set_want(i, state, why):
    want[i] = {'state': state, 'by': why, 'ok': False, 'sent': None, 'tries': 0,
               'warned': False, 'gave_up': False}
    transmit(i)

def transmit(i):
    w = want[i]
    if not dev.get(i, {}).get('online'):
        w['sent'] = None
        log(f"{i}: want {w['state']} ({w['by']}) but light is offline; will send when it returns")
        return
    w['sent'], w['warned'] = time.time(), False
    w['tries'] += 1
    c.publish(f'dashboard/lights/{i}/set',
              json.dumps({'v': 1, 'state': w['state'], 'source': 'engine'}), qos=1)
    log(f"{i}: -> {w['state']} ({w['by']}), try {w['tries']}")

def on_message(cl, ud, m):
    p = m.topic.split('/')
    if len(p) != 4: return
    i, kind = p[2], p[3]
    with lock:
        d = dev.setdefault(i, {'online': False, 'state': None, 'watts': 0.0})
        w = want.get(i)
        if kind == 'availability':
            on = m.payload.decode() == 'online'
            if on != d['online']:
                log(f'{i}: ONLINE' if on else f'{i}: OFFLINE (state is now last-known only)')
            d['online'] = on
            if not on and w: w['ok'] = False          # power blip: re-apply when it returns
            if on and w and not w['ok']:
                w['tries'], w['gave_up'] = 0, False; transmit(i)
        elif kind == 'state':
            try: s = json.loads(m.payload)
            except Exception: return
            d.update(state=s.get('state'), watts=s.get('watts', 0.0))
            if not (w and d['online']): return
            if not w['ok'] and s.get('state') == w['state']:
                w['ok'] = True; log(f"{i}: confirmed {w['state']} ({s.get('watts')} W)")
            elif w['ok'] and s.get('state') != w['state']:
                log(f"{i}: changed to {s.get('state')} by {s.get('cause')}; leaving it until the next edge")

def tick():
    if not clock_ok(): return
    try: rules = [r for r in json.load(open(RULES))['rules'] if r.get('enabled', True)]
    except Exception as e: log(f'rules.json unreadable: {e}'); return
    now, first = datetime.now(), FIRST[0]
    with lock:
        act = {r['id']: active(r, now) for r in rules}
        on_now = {i for r in rules if act[r['id']] for i in r['targets']}
        for r in rules:
            a, was = act[r['id']], prev.get(r['id'])
            if a and (was is not True or first):
                log(f"rule {r['id']}: START" + (' (catch-up at engine start)' if first else ''))
                for i in r['targets']: set_want(i, 'on', r['id'])
            elif not a and was is True:
                log(f"rule {r['id']}: END")
                for i in r['targets']:
                    if i in on_now: log(f'{i}: stays on, another rule still wants it')
                    else: set_want(i, 'off', r['id'])
            prev[r['id']] = a
        for i, w in want.items():
            if w['ok'] or not w['sent']: continue
            age = time.time() - w['sent']
            if age > CONFIRM_S and not w['warned']:
                w['warned'] = True; log(f"{i}: NOT RESPONDING (no confirm of {w['state']} in {CONFIRM_S}s)")
            if age > RETRY_S:
                if w['tries'] < 2: transmit(i)
                elif not w['gave_up']: w['gave_up'] = True; log(f'{i}: giving up until it reconnects')
    FIRST[0] = False
    json.dump(prev, open(STATE, 'w'))

try: c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id='engine-v2')
except AttributeError: c = mqtt.Client(client_id='engine-v2')
c.on_connect = lambda cl, ud, fl, rc, *x: (log(f'broker connected (rc={rc})'),
    cl.subscribe([('dashboard/lights/+/state', 1), ('dashboard/lights/+/availability', 1)]))
c.on_message = on_message
c.connect('127.0.0.1', 1883, 30); c.loop_start()
log('engine-v2 v0.1 started'); time.sleep(2)
while True:
    tick(); time.sleep(TICK_S)
