"""Engine v2 rules API: /api/v2/rules, /api/v2/status, and light commands /api/v2/lights, /api/v2/groups.
Included by main.py. Validates with ruleslib, the same code the engine uses, so they can't disagree."""
import json, os, re, time, fcntl
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException
import ruleslib

HOME = '/home/brifas/engine-v2'
RULES, LOCK, STATUS = f'{HOME}/rules.json', f'{HOME}/rules.lock', '/dev/shm/engine-v2-status.json'
STALE_S = 30
LIGHT_ID = re.compile(r'^[a-z0-9_]+$')               # contract ids; also keeps MQTT wildcards (+ #) out of topics
router = APIRouter(prefix='/api/v2')

class _Locked:                                        # one writer at a time across both uvicorn workers
    def __enter__(self): self.f = open(LOCK, 'w'); fcntl.flock(self.f, fcntl.LOCK_EX); return self
    def __exit__(self, *a): fcntl.flock(self.f, fcntl.LOCK_UN); self.f.close()

def _read():
    try: doc = json.load(open(RULES))
    except FileNotFoundError: return {'v': 1, 'rules': []}
    except Exception as e: raise HTTPException(500, f'rules.json unreadable: {e}')
    if not (isinstance(doc, dict) and doc.get('v') == 1 and isinstance(doc.get('rules'), list)):
        raise HTTPException(500, 'rules.json is not format v1')
    return doc

def _write(doc):
    with open(RULES + '.tmp', 'w') as f:
        json.dump(doc, f, indent=1); f.flush(); os.fsync(f.fileno())
    os.replace(RULES + '.tmp', RULES)

def _check(rule):
    err = ruleslib.check(rule)
    if err: raise HTTPException(422, err)

def _find(doc, rid):
    for i, r in enumerate(doc['rules']):
        if isinstance(r, dict) and r.get('id') == rid: return i
    raise HTTPException(404, f'no rule {rid}')

def _status():
    try: return json.load(open(STATUS))
    except FileNotFoundError: raise HTTPException(503, 'engine status not available (is the engine running?)')
    except Exception as e: raise HTTPException(503, f'engine status unreadable: {e}')

@router.get('/status')
def get_status(): return _status()

@router.get('/rules')
def get_rules(): return _read()

@router.post('/rules')
def create_rule(rule: dict):
    _check(rule)
    with _Locked():
        doc = _read()
        if any(isinstance(r, dict) and r.get('id') == rule['id'] for r in doc['rules']):
            raise HTTPException(409, 'a rule with that id already exists')
        doc['rules'].append(rule); _write(doc)
    return rule

@router.put('/rules/{rid}')
def replace_rule(rid: str, rule: dict):
    if rule.get('id') != rid: raise HTTPException(422, 'id in the body must match the URL')
    _check(rule)
    with _Locked():
        doc = _read(); doc['rules'][_find(doc, rid)] = rule; _write(doc)
    return rule

@router.delete('/rules/{rid}')
def delete_rule(rid: str):
    with _Locked():
        doc = _read(); doc['rules'].pop(_find(doc, rid)); _write(doc)
    return {'ok': True}

@router.post('/rules/{rid}/enabled')
def set_enabled(rid: str, body: dict):
    if type(body.get('enabled')) is not bool: raise HTTPException(422, 'enabled must be true or false')
    with _Locked():
        doc = _read(); r = doc['rules'][_find(doc, rid)]; r['enabled'] = body['enabled']; _write(doc)
    return r

@router.post('/rules/{rid}/skip-next')
def skip_next(rid: str):
    """Skip the run the engine says is next. If the rule is running now, that is today's run,
    so the engine ends it within one tick (the screen calls this STOP & SKIP TODAY)."""
    st = _status()
    if time.time() - st.get('ts', 0) > STALE_S:
        raise HTTPException(409, "the engine isn't running, so the next run can't be known")
    nxt = (st.get('rules', {}).get(rid) or {}).get('next_start')
    if not nxt: raise HTTPException(409, 'no upcoming run to skip')
    keep = (date.today() - timedelta(days=1)).isoformat()      # yesterday stays: an overnight run may still be going
    with _Locked():
        doc = _read(); r = doc['rules'][_find(doc, rid)]
        r['skip_dates'] = sorted({d for d in r.get('skip_dates', []) if d >= keep} | {nxt[:10]})
        _check(r); _write(doc)
    return r

# ---- light commands (Lights-MQTT-Contract v1.2: absolute on/off, QoS 1, never retained, source "ui") ----
# The screens show a change only when the light's own state message confirms it (via status.json).
# The engine sees these commands too; one that goes against a running rule makes that light "changed by hand".
def _fresh_status():
    st = _status()
    if time.time() - st.get('ts', 0) > STALE_S:
        raise HTTPException(503, "the engine isn't running, so lights can't be shown or switched")
    return st

def _want_state(body):
    s = body.get('state')
    if s not in ('on', 'off'): raise HTTPException(422, 'state must be "on" or "off"')
    return s

def _send(ids, state):
    import paho.mqtt.publish as pub                   # imported here so a missing paho can't stop the rules API loading
    msg = json.dumps({'v': 1, 'state': state, 'source': 'ui'})
    try: pub.multiple([{'topic': f'dashboard/lights/{i}/set', 'payload': msg, 'qos': 1, 'retain': False} for i in ids],
                      hostname='127.0.0.1', port=1883)
    except Exception as e: raise HTTPException(502, f'could not reach the MQTT broker: {e}')

@router.post('/lights/{lid}')
def switch_light(lid: str, body: dict):
    state = _want_state(body)
    if not LIGHT_ID.match(lid): raise HTTPException(404, f'no light {lid}')
    d = _fresh_status().get('devices', {}).get(lid)
    if not (d and d.get('in_inventory')): raise HTTPException(404, f'no light {lid}')
    if not d.get('online'): raise HTTPException(409, f"{d.get('name') or lid} is offline")
    _send([lid], state)
    return {'ok': True, 'sent': [lid], 'skipped_offline': []}

@router.post('/groups/{gid}')
def switch_group(gid: str, body: dict):
    state = _want_state(body)
    st = _fresh_status()
    g = st.get('groups', {}).get(gid) if LIGHT_ID.match(gid) else None
    if not g: raise HTTPException(404, f'no group {gid}')
    devs = st.get('devices', {})
    on = [i for i in g['members'] if devs.get(i, {}).get('online')]
    off = [i for i in g['members'] if i not in on]
    if not on: raise HTTPException(409, f"every light in {g.get('name') or gid} is offline")
    _send(on, state)
    return {'ok': True, 'sent': on, 'skipped_offline': off}
