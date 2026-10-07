#!/usr/bin/env python3
"""Automation engine v2, v0.3: clock and sun windows, groups, rules format v1, status.json.
Talks only MQTT, per Lights-MQTT-Contract v1.2 (state is current only while online).
v0.3: a command from a screen (source not "engine") counts as a hand change at once;
a light that stays online but won't confirm is retried every 5 min instead of abandoned;
status.json gives each light "resume": when automation next touches it."""
import json, os, re, time, logging, subprocess, threading
from datetime import datetime
import paho.mqtt.client as mqtt
import ruleslib

VERSION = '0.3'
HOME = os.path.expanduser('~/engine-v2')
RULES, STATE = f'{HOME}/rules.json', f'{HOME}/state.json'
STATUS = '/dev/shm/engine-v2-status.json'           # RAM, rewritten every tick; never touches the NVMe
CONFIRM_S, RETRY_S, TICK_S, RECHECK_S, SLOW_S = 5, 30, 5, 5, 300
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m-%d %H:%M:%S', level=logging.INFO)
log = logging.info
dev, want, lock = {}, {}, threading.Lock()
# state.json = {"active": {rule_id: [device ids]}, "manual": {device id: rule_id}}
# "manual" remembers lights changed by hand during a rule's run, so an engine restart doesn't undo them.
try: _st = json.load(open(STATE))
except Exception: _st = {}
prev, MANUAL = _st.get('active', {}), _st.get('manual', {})
if not (isinstance(prev, dict) and all(isinstance(v, list) for v in prev.values()) and isinstance(MANUAL, dict)):
    prev, MANUAL = {}, {}                              # older or broken format: start clean
FIRST, SAVED = [True], ['']
ERRS, GOOD = [[]], [None]
_clk = {'ok': False, 't': 0}

def rtc_ok():
    """True if the kernel set the clock from the battery-backed RTC at boot and the year is sane.
    A dead or missing battery leaves the RTC invalid, the kernel skips it, and this stays False."""
    try: return open('/sys/class/rtc/rtc0/hctosys').read().strip() == '1' and time.time() > 1767225600  # 2026-01-01
    except OSError: return False

def clock_ok():
    if _clk['ok']: return True
    if time.time() - _clk['t'] < 60: return False
    _clk['t'] = time.time()
    r = subprocess.run(['timedatectl', 'show', '-p', 'NTPSynchronized', '--value'],
                       capture_output=True, text=True).stdout.strip()
    src = 'internet time' if r == 'yes' else ('battery clock (RTC)' if rtc_ok() else None)
    _clk['ok'] = bool(src)
    log(f'clock trusted ({src}): time rules enabled' if src else 'clock NOT trusted (no internet time, no valid RTC): holding time rules')
    return _clk['ok']

def write_atomic(path, text, sync):
    with open(path + '.tmp', 'w') as f:
        f.write(text)
        if sync: f.flush(); os.fsync(f.fileno())
    os.replace(path + '.tmp', path)

def save_state():                                     # only on change; call with the lock held
    s = json.dumps({'active': prev, 'manual': MANUAL}, sort_keys=True)
    if s != SAVED[0]: write_atomic(STATE, s, True); SAVED[0] = s

# ---- inventory: lights that sent a retained config (contract 2) ----
def derive_gid(name):                                 # contract v1.2 fallback when group_id is missing
    return re.sub(r'[^a-z0-9]+', '_', (name or '').lower()).strip('_')

def inventory():
    """(devices, groups) built from configs. Groups: name from the alphabetically first member."""
    inv = {i: d for i, d in dev.items() if d.get('cfg')}
    groups = {}
    for i in sorted(inv):
        c = inv[i]['cfg']
        if not c['group_id']: continue
        g = groups.setdefault(c['group_id'], {'name': c['group'], 'members': [], 'rename_safe': True, 'name_mismatch': False})
        g['members'].append(i)
        g['rename_safe'] &= c['has_gid']
        g['name_mismatch'] |= (c['group'] != g['name'])
    return inv, groups

def expand(r, inv, groups):
    """Rule targets -> (sorted device ids, broken targets)."""
    out, broken = set(), []
    for t in r['targets']:
        if t.startswith('group:'):
            g = groups.get(t[6:])
            if g: out.update(g['members'])
            else: broken.append(t)
        elif t in inv: out.add(t)
        else: broken.append(t)
    return sorted(out), broken

# ---- commands ----
def set_want(i, state, why):
    MANUAL.pop(i, None)                               # a new edge ends any hand override
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

# ---- incoming MQTT ----
def on_message(cl, ud, m):                            # one bad message must not kill the thread
    try: handle(m)
    except Exception as e: log(f'ignored bad message on {m.topic}: {e!r}')

def handle(m):
    p = m.topic.split('/')
    if len(p) != 4: return
    i, kind = p[2], p[3]
    if kind == 'set': return hand_command(i, m)
    with lock:
        d = dev.setdefault(i, {'online': False, 'state': None, 'watts': 0.0, 'cfg': None})
        w = want.get(i)
        if kind == 'config':
            if not m.payload: d['cfg'] = None; log(f'{i}: config cleared (removed from inventory)'); return
            s = json.loads(m.payload)
            if not isinstance(s, dict): raise ValueError('config is not a JSON object')
            gid = s.get('group_id') if isinstance(s.get('group_id'), str) and s.get('group_id') else None
            new = {'name': str(s.get('name') or i), 'group': str(s.get('group') or ''),
                   'group_id': gid or derive_gid(s.get('group')), 'has_gid': bool(gid)}
            if new != d['cfg']: log(f"{i}: config {new['name']!r} in group {new['group_id'] or '-'}"
                                    + ('' if gid or not new['group_id'] else ' (no group_id sent: rename-unsafe)'))
            d['cfg'] = new
        elif kind == 'availability':
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
                w.update(ok=True, manual=False, recheck=None); MANUAL.pop(i, None)
            elif w['ok']:
                w.update(ok=False, manual=True, sent=None); MANUAL[i] = w['by']
                log(f"{i}: changed to {st} by {s.get('cause')}; leaving it until the next edge")
            elif w['recheck'] and not w['manual']:
                log(f'{i}: came back {st}, re-applying {w["state"]}'); transmit(i)

def hand_command(i, m):
    """Someone else sent a command (a screen, simctl). If it goes against what a rule wants,
    that's a hand change: stop enforcing now, not after the light confirms."""
    s = json.loads(m.payload)
    if not isinstance(s, dict) or s.get('source') == 'engine': return
    st = s.get('state')
    if st not in ('on', 'off'): return                # not a contract command (old API format): ignore
    with lock:
        w = want.get(i)
        if not w or w['manual'] or st == w['state']: return
        w.update(manual=True, ok=False, sent=None, recheck=None); MANUAL[i] = w['by']
        log(f"{i}: {st} by hand ({s.get('source')}); leaving it until the next edge")

# ---- the tick ----
def end_targets(rid, tg, on_now, why):
    log(f'rule {rid}: END{why}')
    for i in tg:
        if i in on_now: log(f'{i}: stays on, another rule still wants it')
        else: set_want(i, 'off', rid)

def load_rules():
    rules, errs = ruleslib.load(RULES)
    if errs != ERRS[0]:
        for e in errs: log(f'rules.json problem: {e}')
        if not errs: log('rules.json: no problems')
        ERRS[0] = errs
    if rules is None: rules = GOOD[0]                 # unusable file: keep the last good rules
    if rules is not None: GOOD[0] = rules
    return rules

def tick():
    rules = load_rules()
    now = datetime.now()
    with lock:
        inv, groups = inventory()
        if not clock_ok() or rules is None:
            write_status(rules or [], {}, {}, inv, groups, now); return
        on = [r for r in rules if r.get('enabled', True)]
        exp = {r['id']: expand(r, inv, groups) for r in rules}
        act = {r['id']: ruleslib.active(r, now) for r in on}
        on_now = {i for rid, a in act.items() if a for i in exp[rid][0]}
        first = FIRST[0]
        for rid in [k for k in prev if k not in act]:          # disabled, deleted or invalid mid-window
            end_targets(rid, prev.pop(rid), on_now, ' (disabled or removed)')
        for r in on:
            rid, a, tg = r['id'], act[r['id']], exp[r['id']][0]
            if a and (rid not in prev or first):
                log(f'rule {rid}: START' + (' (catch-up at engine start)' if first else ''))
                for i in tg:
                    if first and rid in prev and MANUAL.get(i) == rid:    # changed by hand before the restart
                        want[i] = {'state': 'on', 'by': rid, 'ok': False, 'sent': None, 'tries': 0, 'warned': False,
                                   'gave_up': False, 'manual': True, 'recheck': None}
                        log(f'{i}: was changed by hand before the restart; leaving it until the next edge')
                    else: set_want(i, 'on', rid)
            elif a and prev[rid] != tg:                         # targets or group membership changed
                gone = [i for i in prev[rid] if i not in tg]
                if gone: end_targets(rid, gone, on_now, ' for removed lights')
                for i in tg:
                    if i not in prev[rid]: set_want(i, 'on', rid)
            elif not a and rid in prev:
                end_targets(rid, prev.pop(rid), on_now, '')
            if a: prev[rid] = tg
        retry()
        for i in [i for i, rid in MANUAL.items() if rid not in prev]: MANUAL.pop(i)   # its run is over
        write_status(rules, act, exp, inv, groups, now)
        FIRST[0] = False
        save_state()

def retry():
    for i, w in want.items():
        if w['ok'] or w['manual']: continue
        if w['recheck'] and time.time() - w['recheck'] > RECHECK_S:
            log(f'{i}: back online but sent no state; re-sending'); transmit(i); continue
        if not w['sent']: continue
        age = time.time() - w['sent']
        if age > CONFIRM_S and not w['warned'] and not w['gave_up']:
            w['warned'] = True; log(f"{i}: NOT RESPONDING (no confirm of {w['state']} in {CONFIRM_S}s)")
        if age > RETRY_S:
            if w['tries'] < 2: transmit(i)
            elif not w['gave_up']:
                w['gave_up'] = True; log(f'{i}: still not responding; retrying every {SLOW_S // 60} min while it stays online')
            elif age > SLOW_S: transmit(i)

# ---- status.json: everything the screens read ----
def iso(t): return t.strftime('%Y-%m-%dT%H:%M') if t else None

def write_status(rules, act, exp, inv, groups, now):
    S = {'v': 1, 'ts': int(time.time()), 'engine': VERSION, 'clock_ok': _clk['ok'],
         'rules': {}, 'problems': {}, 'devices': {}, 'groups': groups}
    try: S['sun'] = dict({'date': now.date().isoformat()},
                         **{k: v.strftime('%H:%M') for k, v in ruleslib.sun_times(now.date()).items()})
    except Exception as e: S['sun'] = None; log(f'sun times failed: {e!r}')
    for e in ERRS[0]:
        rid, _, why = e.partition(': ')
        if ruleslib.ID.match(rid) and why: S['problems'][rid] = why
        else: S['problems']['_file'] = e
    until, resume = {}, {}
    for r in rules:
        rid, on = r['id'], r.get('enabled', True)
        w = ruleslib.next_window(r, now) if on and _clk['ok'] else None
        a = bool(act.get(rid))
        tg, broken = exp.get(rid) or expand(r, inv, groups)
        S['rules'][rid] = {'active': a, 'next_start': iso(w and w[0]), 'next_end': iso(w and w[1]),
                           'broken': broken}
        if a and w: until[rid] = iso(w[1])
        if w:                                          # this rule next touches its lights at its end if running, else its start
            t = iso(w[1] if w[0] <= now else w[0])
            for i in tg:
                if not resume.get(i) or t < resume[i]: resume[i] = t
    for i, d in dev.items():
        w, cfg = want.get(i), d.get('cfg') or {}
        S['devices'][i] = {'name': cfg.get('name', i), 'group': cfg.get('group', ''), 'group_id': cfg.get('group_id', ''),
                           'in_inventory': bool(d.get('cfg')), 'online': d['online'], 'state': d['state'], 'watts': d['watts'],
                           'want': w and w['state'], 'confirmed': bool(w and w['ok']), 'manual': bool(w and w['manual']),
                           'by': w and w['by'], 'until': w and w['state'] == 'on' and until.get(w['by']) or None,
                           'resume': resume.get(i), 'tries': w['tries'] if w else 0}
    write_atomic(STATUS, json.dumps(S), False)

# ---- start ----
try: c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='engine-v2')
except AttributeError: c = mqtt.Client(client_id='engine-v2')
c.on_connect = lambda cl, ud, fl, rc, *x: (log(f'broker connected (rc={rc})'),
    cl.subscribe([('dashboard/lights/+/state', 1), ('dashboard/lights/+/availability', 1), ('dashboard/lights/+/config', 1),
                  ('dashboard/lights/+/set', 1)]))
c.on_message = on_message
c.connect_async('127.0.0.1', 1883, 30); c.loop_start()   # keeps retrying if the broker is down
log(f'engine-v2 v{VERSION} started'); time.sleep(2)
while True:
    try: tick()
    except Exception as e: log(f'tick failed: {e!r}')       # one bad rule must not kill the engine
    time.sleep(TICK_S)
