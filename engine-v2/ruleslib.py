"""Rules format v1 (Engine-v2 handoff 4.1): load, validate, window math.
Shared by the engine and (Segment 2) the API, so both validate the same way."""
import json, re
from datetime import datetime, date, time, timedelta
from functools import lru_cache
from astral import LocationInfo
from astral.sun import sun

LOC = LocationInfo('Tallmansville', 'WV', 'America/New_York', 38.8376, -80.1284)
DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
SUN = ('dawn', 'sunrise', 'sunset', 'dusk')
KEYS = {'id', 'enabled', 'targets', 'state', 'start', 'end', 'days', 'skip_dates', 'dates'}
ID = re.compile(r'^[a-z0-9_]+$')
TARGET = re.compile(r'^(group:)?[a-z0-9_]+$')
CLOCK = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
MD = re.compile(r'^\d{2}-\d{2}$')

@lru_cache(maxsize=64)
def sun_times(d):
    """Local wall-clock times (naive) of dawn, sunrise, sunset, dusk on date d."""
    s = sun(LOC.observer, date=d, tzinfo=LOC.timezone)
    return {k: s[k].replace(tzinfo=None) for k in SUN}

def edge_key(e):
    return ('clock', e['clock']) if 'clock' in e else ('sun', e['sun'], e.get('offset_min', 0))

def check_edge(e, name):
    if not isinstance(e, dict): return f'{name} must be an object'
    if ('clock' in e) == ('sun' in e): return f'{name} needs exactly one of clock or sun'
    if 'clock' in e:
        if set(e) != {'clock'}: return f'{name}: clock takes no other keys'
        if not (isinstance(e['clock'], str) and CLOCK.match(e['clock'])): return f'{name}.clock must be HH:MM, 24 h'
        return None
    if set(e) - {'sun', 'offset_min'}: return f'{name}: sun takes only offset_min'
    if e['sun'] not in SUN: return f'{name}.sun must be one of: ' + ', '.join(SUN)
    o = e.get('offset_min', 0)
    if type(o) is not int or abs(o) > 720: return f'{name}.offset_min must be a whole number, -720 to 720'
    return None

def check(r):
    """None if rule r is valid format v1, else a short reason."""
    if not isinstance(r, dict): return 'rule must be an object'
    if not (isinstance(r.get('id'), str) and ID.match(r['id'])): return 'id must be lowercase a-z 0-9 _'
    extra = set(r) - KEYS
    if extra: return 'unknown keys: ' + ', '.join(sorted(extra))
    if type(r.get('enabled', True)) is not bool: return 'enabled must be true or false'
    t = r.get('targets')
    if not (isinstance(t, list) and t and all(isinstance(x, str) and TARGET.match(x) for x in t)):
        return 'targets must be a non-empty list of light ids or group:<id>'
    if r.get('state') != 'on': return 'state must be "on"'
    for k in ('start', 'end'):
        err = check_edge(r.get(k), k)
        if err: return err
    if edge_key(r['start']) == edge_key(r['end']): return 'start and end are the same'
    d = r.get('days', DAYS)
    if not (isinstance(d, list) and d and all(x in DAYS for x in d)): return 'days must be a non-empty list of mon..sun'
    s = r.get('skip_dates', [])
    if not (isinstance(s, list) and all(isinstance(x, str) and DATE.match(x) for x in s)):
        return 'skip_dates must be a list of YYYY-MM-DD'
    try: [date.fromisoformat(x) for x in s]
    except ValueError: return 'skip_dates has an impossible date'
    return check_dates(r.get('dates'))

def check_dates(g):
    """Optional date range: {"from", "until", "yearly"}. Yearly uses MM-DD, one-time uses YYYY-MM-DD."""
    if g is None: return None
    if not (isinstance(g, dict) and set(g) == {'from', 'until', 'yearly'} and type(g['yearly']) is bool):
        return 'dates must be {"from", "until", "yearly"}'
    pat, fix = (MD, '2024-') if g['yearly'] else (DATE, '')      # 2024 is a leap year, so 02-29 is allowed
    if not all(isinstance(g[k], str) and pat.match(g[k]) for k in ('from', 'until')):
        return 'dates.from/until must be ' + ('MM-DD' if g['yearly'] else 'YYYY-MM-DD')
    try: a, b = date.fromisoformat(fix + g['from']), date.fromisoformat(fix + g['until'])
    except ValueError: return 'dates has an impossible date'
    if not g['yearly'] and a > b: return 'dates: from is after until'
    return None

def in_range(r, d):
    g = r.get('dates')
    if not g: return True
    if not g['yearly']: return g['from'] <= d.isoformat() <= g['until']
    md = d.isoformat()[5:]
    if g['from'] <= g['until']: return g['from'] <= md <= g['until']
    return md >= g['from'] or md <= g['until']                  # wraps the new year, e.g. Aug 20 - Jun 5

def load(path):
    """(rules, errors). rules is None if the whole file is unusable: keep the last good set.
    A missing file means no rules. Invalid rules are left out and reported. Never raises."""
    try: doc = json.load(open(path))
    except FileNotFoundError: return [], []
    except Exception as e: return None, [f'file unreadable: {e}']
    if not (isinstance(doc, dict) and doc.get('v') == 1 and isinstance(doc.get('rules'), list)):
        return None, ['file must be {"v": 1, "rules": [...]}']
    good, errs, seen = [], [], set()
    for n, r in enumerate(doc['rules']):
        rid = r.get('id') if isinstance(r, dict) and isinstance(r.get('id'), str) else f'rule #{n + 1}'
        err = check(r) or ('duplicate id' if rid in seen else None)
        if err: errs.append(f'{rid}: {err}'); continue
        seen.add(rid); good.append(r)
    return good, errs

def edge(e, d):
    if 'clock' in e:
        h, m = map(int, e['clock'].split(':')); return datetime.combine(d, time(h, m))
    return sun_times(d)[e['sun']] + timedelta(minutes=e.get('offset_min', 0))

def window(r, d):
    """(start, end) of the window that belongs to date d, or None if d is not a run day.
    The end is the first end time after the start (so windows can cross midnight)."""
    if DAYS[d.weekday()] not in r.get('days', DAYS) or d.isoformat() in r.get('skip_dates', []) or not in_range(r, d):
        return None
    s = edge(r['start'], d)
    for k in range(3):
        e = edge(r['end'], d + timedelta(days=k))
        if e > s: return s, e
    return None

def active(r, now):
    for k in (0, 1, 2):
        w = window(r, now.date() - timedelta(days=k))
        if w and w[0] <= now < w[1]: return True
    return False

def next_window(r, now):
    """The current window if active, else the next one within about a year, or None."""
    for k in range(-2, 400):
        w = window(r, now.date() + timedelta(days=k))
        if w and w[1] > now: return w
    return None
