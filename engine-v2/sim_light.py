#!/usr/bin/env python3
"""Simulated light per Lights-MQTT-Contract v1. Behaves like a Shelly behind the adapter."""
import json, os, sys, time, random, threading, argparse
import paho.mqtt.client as mqtt

ap = argparse.ArgumentParser()
ap.add_argument('--id', default='front_door_flood')
ap.add_argument('--name', default='Front Door')
ap.add_argument('--group', default='Outdoor Flood Lights')
ap.add_argument('--host', default='127.0.0.1')
ap.add_argument('--port', type=int, default=1884)
a = ap.parse_args()
pw = os.environ.get('SIM_PASS')
if not pw:
    sys.exit('Set the devices password first:  read -s SIM_PASS; export SIM_PASS')

T = f'dashboard/lights/{a.id}/'
S = {'state': 'off', 'mode': 'normal'}  # mode: normal | silent | deadbulb

def watts():
    if S['state'] == 'off' or S['mode'] == 'deadbulb':
        return 0.0
    return round(78 + random.uniform(-1.5, 1.5), 1)

def pub_state(cause):
    w = watts()
    c.publish(T + 'state', json.dumps({'v': 1, 'state': S['state'], 'watts': w, 'cause': cause}),
              qos=1, retain=True)
    print(f"  -> state {S['state']} ({cause}, {w} W)")

def on_connect(cl, ud, flags, rc, *x):
    if rc != 0:
        print('connect failed, rc', rc); return
    cl.publish(T + 'availability', 'online', qos=1, retain=True)
    cl.publish(T + 'config', json.dumps({'v': 1, 'id': a.id, 'name': a.name, 'group': a.group,
               'capabilities': ['onoff', 'power']}), qos=1, retain=True)
    pub_state('boot'); cl.subscribe(T + 'set', qos=1); print(f'{a.id} online')

def on_message(cl, ud, m):
    try: want = json.loads(m.payload).get('state')
    except Exception: print('  bad set payload'); return
    print(f'  <- set {want}')
    if want not in ('on', 'off'): return
    if S['mode'] == 'silent': print('  (silent: ignoring)'); return
    def act():
        time.sleep(0.5); S['state'] = want; pub_state('command')
    threading.Thread(target=act, daemon=True).start()

try: c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=f'sim-{a.id}')
except AttributeError: c = mqtt.Client(client_id=f'sim-{a.id}')
c.username_pw_set('devices', pw)
c.will_set(T + 'availability', 'offline', qos=1, retain=True)
c.on_connect = on_connect; c.on_message = on_message
c.connect(a.host, a.port, keepalive=15); c.loop_start()
print('commands: switch | silent | deadbulb | normal | drop | quit')
for line in sys.stdin:
    cmd = line.strip()
    if cmd == 'switch':
        S['state'] = 'off' if S['state'] == 'on' else 'on'; pub_state('switch')
    elif cmd in ('silent', 'deadbulb', 'normal'):
        S['mode'] = cmd; print('  mode:', cmd, '(deadbulb applies on next "on")' if cmd == 'deadbulb' else '')
    elif cmd == 'drop':
        print('  power loss: broker will publish offline'); os._exit(1)
    elif cmd == 'quit':
        c.publish(T + 'availability', 'offline', qos=1, retain=True).wait_for_publish()
        c.disconnect(); break
