#!/usr/bin/env python3
import json
import time
import sqlite3
import logging
import requests
import datetime
import threading
from astral import LocationInfo
from astral.sun import sun

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

DB_PATH = '/home/brifas/dashboard.db'
API_URL = 'http://localhost:8000'

LOCATION = LocationInfo(
    name='Tallmansville', region='WV',
    timezone='America/New_York',
    latitude=38.8376, longitude=-80.1284
)

def db():
    return sqlite3.connect(DB_PATH)

def get_rules():
    try:
        conn = db()
        rows = conn.execute(
            'SELECT id,name,category,enabled,trigger_type,trigger_config,conditions,actions FROM automation_rules WHERE enabled=1'
        ).fetchall()
        conn.close()
        rules = []
        for r in rows:
            rules.append({
                'id': r[0], 'name': r[1], 'category': r[2],
                'enabled': r[3], 'trigger_type': r[4],
                'trigger_config': json.loads(r[5]),
                'conditions': json.loads(r[6]),
                'actions': json.loads(r[7])
            })
        return rules
    except Exception as e:
        log.error(f'get_rules error: {e}')
        return []

def log_result(rule_id, rule_name, result, detail=''):
    try:
        conn = db()
        conn.execute(
            'INSERT INTO automation_log (timestamp,rule_id,rule_name,result,detail) VALUES (?,?,?,?,?)',
            (int(time.time()), rule_id, rule_name, result, detail)
        )
        conn.execute(
            'UPDATE automation_rules SET last_triggered=? WHERE id=?',
            (int(time.time()), rule_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f'log_result error: {e}')

def get_sensor_value(sensor_id):
    try:
        r = requests.get(f'{API_URL}/api/sensors', timeout=5)
        sensors = r.json().get('sensors', [])
        for s in sensors:
            if s['id'] == sensor_id:
                return s['last_value']
    except:
        pass
    return None

def get_solar_times():
    try:
        today = datetime.date.today()
        s = sun(LOCATION.observer, date=today, tzinfo=LOCATION.timezone)
        return {
            'sunrise': s['sunrise'],
            'sunset': s['sunset'],
            'dawn': s['dawn'],
            'dusk': s['dusk']
        }
    except Exception as e:
        log.error(f'solar error: {e}')
        return {}

def check_conditions(conditions):
    if not conditions:
        return True
    now = datetime.datetime.now()
    for cond in conditions:
        ctype = cond.get('type')
        if ctype == 'time_range':
            start = datetime.time.fromisoformat(cond['start'])
            end = datetime.time.fromisoformat(cond['end'])
            t = now.time()
            in_range = start <= t <= end if start <= end else t >= start or t <= end
            if not in_range:
                return False
        elif ctype == 'sensor_threshold':
            val = get_sensor_value(cond['sensor_id'])
            if val is None:
                return False
            op = cond.get('operator', 'gt')
            threshold = cond['value']
            if op == 'gt' and not val > threshold: return False
            if op == 'lt' and not val < threshold: return False
            if op == 'eq' and not val == threshold: return False
    return True

def execute_actions(actions, rule_name):
    for action in actions:
        atype = action.get('type')
        try:
            if atype == 'light_control':
                requests.post(
                    f'{API_URL}/api/lights/{action["device_id"]}/control',
                    json=action.get('command', {}), timeout=5
                )
            elif atype == 'system_control':
                requests.post(
                    f'{API_URL}/api/systems/{action["system_id"]}/control',
                    json=action.get('command', {}), timeout=5
                )
            elif atype == 'notification':
                log.info(f'NOTIFICATION [{rule_name}]: {action.get("message","")}')
            log.info(f'Action executed: {atype}')
        except Exception as e:
            log.error(f'Action error {atype}: {e}')

class ScheduleTrigger:
    def __init__(self):
        self._fired = {}

    def check(self, rule):
        cfg = rule['trigger_config']
        now = datetime.datetime.now()
        trigger_time = datetime.time.fromisoformat(cfg['time'])
        days = cfg.get('days', [0,1,2,3,4,5,6])
        if now.weekday() not in days:
            return False
        key = rule['id'] + '_' + now.strftime('%Y%m%d')
        if key in self._fired:
            return False
        if now.time().hour == trigger_time.hour and now.time().minute == trigger_time.minute:
            self._fired[key] = True
            return True
        return False

class SolarTrigger:
    def __init__(self):
        self._fired = {}
        self._solar = {}
        self._solar_date = None

    def _refresh_solar(self):
        today = datetime.date.today()
        if self._solar_date != today:
            self._solar = get_solar_times()
            self._solar_date = today

    def check(self, rule):
        cfg = rule['trigger_config']
        self._refresh_solar()
        event = cfg.get('event', 'sunrise')
        offset = cfg.get('offset_minutes', 0)
        base = self._solar.get(event)
        if not base:
            return False
        target = base + datetime.timedelta(minutes=offset)
        now = datetime.datetime.now(target.tzinfo)
        key = rule['id'] + '_' + now.strftime('%Y%m%d')
        if key in self._fired:
            return False
        diff = abs((now - target).total_seconds())
        if diff < 30:
            self._fired[key] = True
            return True
        return False

class SensorTrigger:
    def __init__(self):
        self._last_state = {}

    def check(self, rule):
        cfg = rule['trigger_config']
        sensor_id = cfg.get('sensor_id')
        op = cfg.get('operator', 'gt')
        threshold = cfg.get('value', 0)
        val = get_sensor_value(sensor_id)
        if val is None:
            return False
        triggered = False
        if op == 'gt': triggered = val > threshold
        if op == 'lt': triggered = val < threshold
        if op == 'eq': triggered = val == threshold
        prev = self._last_state.get(rule['id'], False)
        self._last_state[rule['id']] = triggered
        return triggered and not prev

def main():
    log.info('Automation engine starting...')
    schedule_trigger = ScheduleTrigger()
    solar_trigger = SolarTrigger()
    sensor_trigger = SensorTrigger()

    while True:
        try:
            rules = get_rules()
            for rule in rules:
                ttype = rule['trigger_type']
                fired = False
                if ttype == 'schedule':
                    fired = schedule_trigger.check(rule)
                elif ttype == 'solar':
                    fired = solar_trigger.check(rule)
                elif ttype == 'sensor':
                    fired = sensor_trigger.check(rule)
                elif ttype == 'manual':
                    pass
                if fired:
                    log.info(f'Rule triggered: {rule["name"]}')
                    if check_conditions(rule['conditions']):
                        execute_actions(rule['actions'], rule['name'])
                        log_result(rule['id'], rule['name'], 'executed')
                    else:
                        log_result(rule['id'], rule['name'], 'skipped', 'conditions not met')
        except Exception as e:
            log.error(f'Engine loop error: {e}')
        time.sleep(30)

if __name__ == '__main__':
    main()
