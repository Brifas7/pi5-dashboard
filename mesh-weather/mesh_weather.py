#!/usr/bin/env python3
"""Mesh weather reader: XIAO ESP32S3 + Wio-SX1262 (Meshtastic) on USB.
Local BME680 -> wx_* sensors (wx_temp, wx_humidity, ...), system wx_station.
Allowlisted remote mesh nodes -> wx_<node>_* sensors. Replaces rak_reader.py."""
import glob, json, math, os, sys, time, logging, threading
import requests
import meshtastic, meshtastic.serial_interface
from pubsub import pub

API = 'http://localhost:8000'
HOME = os.path.expanduser('~/mesh-weather')
REMOTES = f'{HOME}/remote_nodes.json'
LAST_REBOOT = f'{HOME}/.last_reboot'
WATCHDOG_S = 75 * 60          # no local environment telemetry this long -> reboot the node
REBOOT_GAP_S = 60 * 60        # at most one watchdog reboot per hour
LOCAL = {'id': 'wx_station', 'prefix': 'wx', 'name': 'Weather Station',
         'summary': 'XIAO ESP32S3 + Wio-SX1262 + BME680 (Meshtastic)'}
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('mesh-weather')
state = {'last_local': time.time(), 'iface': None, 'my': None, 'port': None}
heard, announced = {}, set()

def c_to_f(c): return round(c * 9 / 5 + 32, 1)

def dew_c(t, rh):
    a, b = 17.27, 237.7
    al = a * t / (b + t) + math.log(max(rh, 1) / 100.0)
    return b * al / (a - al)

def find_port():
    p = os.environ.get('MESH_PORT')
    if p: return p
    for pat in ('/dev/serial/by-id/*Espressif*', '/dev/serial/by-id/*'):
        m = sorted(glob.glob(pat))
        if m: return m[0]
    return '/dev/ttyACM0'

def remotes():
    try: return json.load(open(REMOTES))
    except FileNotFoundError: return {}
    except Exception as e: log.error(f'remote_nodes.json unreadable: {e}'); return {}

def post(path, body):
    try:
        r = requests.post(API + path, json=body, timeout=5)
        return r.ok and r.json().get('success', True)
    except Exception as e:
        log.warning(f'API {path} failed: {e}'); return False

def register(st, where):
    # Every report re-registers: keeps last_seen current so Operations shows online/offline correctly.
    ok = post('/api/devices/register', {'id': st['id'], 'name': st['name'], 'category': 'system',
              'type': 'weather_station', 'summary': st['summary'], 'ip': where})
    if ok and st['id'] not in announced:
        announced.add(st['id']); log.info(f"registered {st['id']} ({st['name']})")

def handle_env(st, env, where):
    local = st is LOCAL
    lab = (lambda s: s) if local else (lambda s: f"{st['name']} {s}")
    p, r = st['prefix'], []
    t, rh = env.get('temperature'), env.get('relativeHumidity')
    if t is not None:
        r.append({'id': f'{p}_temp', 'name': lab('Temperature'), 'value': c_to_f(t), 'unit': '°F'})
    if rh is not None:
        r.append({'id': f'{p}_humidity', 'name': lab('Humidity'), 'value': round(rh, 1), 'unit': '%'})
    if env.get('barometricPressure') is not None:
        r.append({'id': f'{p}_pressure', 'name': lab('Pressure'),
                  'value': round(env['barometricPressure'], 1), 'unit': 'hPa'})
    if t is not None and rh:
        r.append({'id': f'{p}_dewpoint', 'name': lab('Dew Point'), 'value': c_to_f(dew_c(t, rh)), 'unit': '°F'})
    if env.get('iaq') is not None:
        r.append({'id': f'{p}_airquality', 'name': lab('Air Quality'), 'value': round(env['iaq'], 1), 'unit': 'IAQ'})
    if r and post('/api/sensors/ingest', {'readings': r}):
        log.info(f"{st['name']}: " + ', '.join(f"{x['id']}={x['value']}" for x in r))
    register(st, where)

def handle_dev(st, d):
    p, r = st['prefix'], []
    if d.get('batteryLevel') is not None:
        r.append({'id': f'{p}_battery', 'name': f"{st['name']} Battery", 'value': d['batteryLevel'], 'unit': '%'})
    if d.get('voltage') is not None:
        r.append({'id': f'{p}_voltage', 'name': f"{st['name']} Voltage", 'value': round(d['voltage'], 2), 'unit': 'V'})
    if r and post('/api/sensors/ingest', {'readings': r}):
        log.info(f"{st['name']}: " + ', '.join(f"{x['id']}={x['value']}" for x in r))

def on_telemetry(packet, interface):
    try:
        tel = packet.get('decoded', {}).get('telemetry', {})
        env, devm = tel.get('environmentMetrics'), tel.get('deviceMetrics')
        fid = packet.get('fromId') or ''
        if packet.get('from') == state['my']:
            if env:
                state['last_local'] = time.time()
                handle_env(LOCAL, env, str(state['port']))
            return                                    # local device metrics: USB powered, not useful
        rem = remotes()
        if fid not in rem:
            if time.time() - heard.get(fid, 0) > 3600:
                heard[fid] = time.time()
                nm = (interface.nodes or {}).get(fid, {}).get('user', {}).get('longName', '?')
                log.info(f'heard telemetry from {fid} ({nm}); not in remote_nodes.json, ignored')
            return
        key = fid.lstrip('!').lower()
        st = {'id': f'wx_{key}', 'prefix': f'wx_{key}', 'name': rem[fid], 'summary': f'Mesh node {fid}'}
        if env: handle_env(st, env, 'mesh')
        if devm: handle_dev(st, devm)
    except Exception as e:
        log.error(f'telemetry error: {e}')

def on_lost(interface):
    log.error('serial connection lost; exiting so systemd reconnects cleanly'); os._exit(1)

def watchdog():
    while True:
        time.sleep(60)
        idle = time.time() - state['last_local']
        if idle < WATCHDOG_S: continue
        try: last = float(open(LAST_REBOOT).read())
        except Exception: last = 0
        if time.time() - last >= REBOOT_GAP_S:
            open(LAST_REBOOT, 'w').write(str(time.time()))
            log.error(f'WATCHDOG: no local telemetry for {int(idle / 60)} min; rebooting the node')
            try: state['iface'].localNode.reboot(5)
            except Exception as e: log.error(f'reboot command failed: {e}')
            time.sleep(10); os._exit(1)
        log.error(f'no local telemetry for {int(idle / 60)} min (node already rebooted within the hour; waiting)')
        state['last_local'] = time.time()             # throttle this message to every 15 min

def main():
    os.makedirs(HOME, exist_ok=True)
    state['port'] = p = find_port()
    log.info(f'connecting to Meshtastic node on {p}')
    pub.subscribe(on_telemetry, 'meshtastic.receive.telemetry')
    pub.subscribe(on_lost, 'meshtastic.connection.lost')
    try:
        iface = meshtastic.serial_interface.SerialInterface(p)
    except Exception as e:
        log.error(f'cannot open {p}: {e}'); time.sleep(5); sys.exit(1)
    state['iface'] = iface
    state['my'] = getattr(getattr(iface, 'myInfo', None), 'my_node_num', None)
    if state['my'] is None:
        log.error('no local node number; cannot tell local from remote; exiting'); sys.exit(1)
    log.info(f"connected; local node {state['my']}; remote allowlist: {list(remotes()) or 'none'}")
    state['last_local'] = time.time()
    threading.Thread(target=watchdog, daemon=True).start()
    while True: time.sleep(1)

if __name__ == '__main__':
    main()
