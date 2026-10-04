#!/usr/bin/env python3
"""Write a test rules.json:  mkrule.py clock | sun | mix | group   (windows open 1-2 min from now)"""
import json, os, sys
from datetime import datetime, timedelta
import ruleslib as L

now = datetime.now().replace(second=0, microsecond=0)
def clock(m): return {'clock': (now + timedelta(minutes=m)).strftime('%H:%M')}
def sun(m):                    # nearest sun event, with the offset that lands m minutes from now
    t, st = now + timedelta(minutes=m), L.sun_times(now.date())
    ev = min(L.SUN, key=lambda k: abs((t - st[k]).total_seconds()))
    return {'sun': ev, 'offset_min': round((t - st[ev]).total_seconds() / 60)}
def day(n): return (now + timedelta(days=n)).date().isoformat()
def R(i, s, e, **k): return dict(id=i, enabled=True, targets=['front_door_flood'], state='on', start=s, end=e, **k)

mode = sys.argv[1] if len(sys.argv) > 1 else ''
if mode == 'clock': rules = [R('test_window', clock(2), clock(8))]
elif mode == 'sun': rules = [R('test_sun', sun(2), sun(8))]
elif mode == 'mix': rules = [R('test_sun', sun(1), sun(3)),
                             R('test_skip', clock(-5), clock(30), skip_dates=[now.date().isoformat()]),
                             R('test_dates', clock(-5), clock(30), dates={'from': day(1), 'until': day(5), 'yearly': False}),
                             dict(R('test_bad', clock(-5), clock(30)), state='off')]
elif mode == 'group': rules = [dict(R('test_group', clock(1), clock(10)), targets=['group:outdoor_flood_lights'])]
else: sys.exit('usage: mkrule.py clock | sun | mix | group')
for r in rules:
    err = L.check(r)
    if err and r['id'] != 'test_bad': sys.exit(f"{r['id']}: {err}")
json.dump({'v': 1, 'rules': rules}, open(os.path.expanduser('~/engine-v2/rules.json'), 'w'), indent=1)
for r in rules: print(r['id'], json.dumps(r['start']), '->', json.dumps(r['end']), r.get('skip_dates', ''))
