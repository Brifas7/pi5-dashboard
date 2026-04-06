from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
import subprocess
import json
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/system")
def system_stats():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    try:
        temp_output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        cpu_temp = float(temp_output.replace("temp=","").replace("'C\n",""))
    except:
        cpu_temp = 0.0
    return {
        "cpu_percent": cpu,
        "cpu_temp": cpu_temp,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / 1024**3, 1),
        "ram_total_gb": round(ram.total / 1024**3, 1),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / 1024**3, 1),
        "disk_total_gb": round(disk.total / 1024**3, 1),
        "hailo_percent": 0,
    }

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/events")
async def get_events():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:5000/api/events?limit=5", timeout=3)
            events = r.json()
            result = []
            for e in events:
                result.append({
                    "camera": e.get("camera", ""),
                    "label": e.get("label", ""),
                    "score": round(e.get("score", 0) * 100),
                    "time": e.get("start_time", 0)
                })
            return result
    except:
        return []
@app.post("/api/exit-kiosk")
def exit_kiosk():
    subprocess.Popen(["pkill", "chromium"])
    return {"status": "exiting"}

@app.get("/api/cameras")
async def get_cameras():
    try:
        async with httpx.AsyncClient() as client:
            config_r = await client.get("http://localhost:5000/api/config", timeout=5)
            config = config_r.json()
            cam_names = list(config.get("cameras", {}).keys())
            stats_r = await client.get("http://localhost:5000/api/stats", timeout=5)
            stats = stats_r.json()
            cam_stats = stats.get("cameras", {})
            result = []
            for name in cam_names:
                fps = cam_stats.get(name, {}).get("camera_fps", 0)
                result.append({"name": name, "online": fps > 0})
            return {"cameras": result}
    except Exception as e:
        return {"cameras": [], "error": str(e)}

@app.get("/api/clips")
async def get_clips(camera: str = None, label: str = None, limit: int = 100):
    try:
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:5000/api/events?limit={limit}&has_clip=1&include_thumbnails=1"
            if camera and camera != "all":
                url += f"&camera={camera}"
            if label and label != "all":
                url += f"&label={label}"
            r = await client.get(url, timeout=10)
            events = r.json()
            clips = []
            for e in events:
                start = e.get("start_time", 0)
                end = e.get("end_time") or start
                dur = round(end - start) if end > start else 0
                clips.append({
                    "id": e["id"],
                    "camera": e["camera"],
                    "label": e.get("label", "unknown"),
                    "score": round((e.get("top_score") or 0) * 100),
                    "start_time": start,
                    "duration": f"{dur // 60:02d}:{dur % 60:02d}",
                    "thumbnail": f"http://localhost:5000/api/events/{e['id']}/thumbnail.jpg",
                    "clip_url": f"http://localhost:5000/api/events/{e['id']}/clip.mp4"
                })
            return {"clips": clips}
    except Exception as e:
        return {"clips": [], "error": str(e)}

@app.delete("/api/clips/{event_id}")
async def delete_clip(event_id: str):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.delete(f"http://localhost:5000/api/events/{event_id}", timeout=5)
            return {"success": r.status_code == 200}
    except Exception as e:
        return {"success": False, "error": str(e)}
@app.get("/api/lights")
async def get_lights():
    # Returns registered lighting devices
    # Empty until devices are registered via MQTT/device registry
    return {"devices": []}

@app.post("/api/lights/{device_id}/control")
async def control_light(device_id: str, command: dict):
    # Will send commands to ESP32/Pi Pico via MQTT
    # Placeholder until hardware is connected
    return {"success": True, "device_id": device_id, "command": command}

@app.get("/api/lights")
async def get_lights():
    # Returns registered lighting devices
    # Empty until devices are registered via MQTT/device registry
    return {"devices": []}

@app.post("/api/lights/{device_id}/control")
async def control_light(device_id: str, command: dict):
    # Will send commands to ESP32/Pi Pico via MQTT
    # Placeholder until hardware is connected
    return {"success": True, "device_id": device_id, "command": command}

@app.get("/api/systems")
async def get_systems():
    return {"systems": []}

@app.post("/api/systems/{system_id}/control")
async def control_system(system_id: str, command: dict):
    return {"success": True, "system_id": system_id, "command": command}

@app.post("/api/brightness")
async def set_brightness(payload: dict):
    val = int(payload.get("value", 80))
    subprocess.Popen(["ddcutil", "setvcp", "10", str(val)])
    return {"success": True, "value": val}

@app.post("/api/display")
async def set_display(payload: dict):
    state = payload.get("state", "on")
    val = "1" if state == "on" else "0"
    subprocess.Popen(["vcgencmd", "display_power", val])
    return {"success": True, "state": state}

@app.get("/api/sysinfo")
async def sysinfo():
    try:
        hostname = subprocess.check_output(["hostname"]).decode().strip()
        ip_out = subprocess.check_output(["hostname", "-I"]).decode().strip().split()
        ip = next((i for i in ip_out if i.startswith("192.168.1.")), ip_out[0] if ip_out else "unknown")
        uptime = subprocess.check_output(["uptime", "-p"]).decode().strip()
        return {"hostname": hostname, "ip": ip, "tailscale": "100.76.61.67", "uptime": uptime}
    except Exception as e:
        return {"hostname": "pi5-dashboard", "ip": "192.168.1.234", "tailscale": "100.76.61.67", "uptime": "unknown"}

import sqlite3
import time as _time

DB_PATH = "/home/brifas/dashboard.db"

def _db():
    return sqlite3.connect(DB_PATH)

@app.get("/api/sensors")
def get_sensors():
    try:
        conn = _db()
        rows = conn.execute(
            "SELECT id, name, unit, source, last_seen, last_value FROM sensor_registry"
        ).fetchall()
        conn.close()
        sensors = []
        for r in rows:
            sensors.append({
                "id": r[0], "name": r[1], "unit": r[2],
                "source": r[3], "last_seen": r[4], "last_value": r[5]
            })
        return {"sensors": sensors}
    except Exception as e:
        return {"sensors": [], "error": str(e)}

@app.get("/api/sensors/{sensor_id}/history")
def get_sensor_history(sensor_id: str, range: str = "24h"):
    try:
        ranges = {"24h": 86400, "7d": 604800, "30d": 2592000, "6m": 15552000, "1y": 31536000}
        seconds = ranges.get(range, 86400)
        since = int(_time.time()) - seconds
        conn = _db()
        rows = conn.execute(
            "SELECT timestamp, value FROM sensor_readings WHERE sensor_id=? AND timestamp>? ORDER BY timestamp ASC",
            (sensor_id, since)
        ).fetchall()
        conn.close()
        return {"sensor_id": sensor_id, "range": range, "points": [{"t": r[0], "v": r[1]} for r in rows]}
    except Exception as e:
        return {"points": [], "error": str(e)}

@app.post("/api/sensors/ingest")
def ingest_sensor(payload: dict):
    try:
        now = int(_time.time())
        conn = _db()
        for reading in payload.get("readings", []):
            sid = reading["id"]
            val = reading["value"]
            conn.execute(
                "INSERT INTO sensor_readings (timestamp, sensor_id, sensor_name, value, unit) VALUES (?,?,?,?,?)",
                (now, sid, reading.get("name",""), val, reading.get("unit",""))
            )
            conn.execute(
                "UPDATE sensor_registry SET last_seen=?, last_value=? WHERE id=?",
                (now, val, sid)
            )
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

from astral import LocationInfo
from astral.sun import sun
from astral.moon import phase as moon_phase
import datetime

LOCATION = LocationInfo(
    name="Tallmansville",
    region="WV",
    timezone="America/New_York",
    latitude=38.8376,
    longitude=-80.1284
)

@app.get("/api/solar")
def get_solar():
    try:
        today = datetime.date.today()
        s = sun(LOCATION.observer, date=today, tzinfo=LOCATION.timezone)
        mp = moon_phase(today)
        if mp < 1: phase_name = "New Moon"
        elif mp < 7: phase_name = "Waxing Crescent"
        elif mp < 8: phase_name = "First Quarter"
        elif mp < 14: phase_name = "Waxing Gibbous"
        elif mp < 15: phase_name = "Full Moon"
        elif mp < 21: phase_name = "Waning Gibbous"
        elif mp < 22: phase_name = "Last Quarter"
        else: phase_name = "Waning Crescent"
        phase_icons = {
            "New Moon": "🌑", "Waxing Crescent": "🌒", "First Quarter": "🌓",
            "Waxing Gibbous": "🌔", "Full Moon": "🌕", "Waning Gibbous": "🌖",
            "Last Quarter": "🌗", "Waning Crescent": "🌘"
        }
        return {
            "sunrise": s["sunrise"].strftime("%H:%M"),
            "sunset": s["sunset"].strftime("%H:%M"),
            "dawn": s["dawn"].strftime("%H:%M"),
            "dusk": s["dusk"].strftime("%H:%M"),
            "solar_noon": s["noon"].strftime("%H:%M"),
            "moon_phase": round(mp, 1),
            "moon_phase_name": phase_name,
            "moon_icon": phase_icons[phase_name]
        }
    except Exception as e:
        return {"error": str(e)}

from astral import LocationInfo
from astral.sun import sun
from astral.moon import phase as moon_phase
import datetime

LOCATION = LocationInfo(
    name="Tallmansville",
    region="WV",
    timezone="America/New_York",
    latitude=38.8376,
    longitude=-80.1284
)

@app.get("/api/solar")
def get_solar():
    try:
        today = datetime.date.today()
        s = sun(LOCATION.observer, date=today, tzinfo=LOCATION.timezone)
        mp = moon_phase(today)
        if mp < 1: phase_name = "New Moon"
        elif mp < 7: phase_name = "Waxing Crescent"
        elif mp < 8: phase_name = "First Quarter"
        elif mp < 14: phase_name = "Waxing Gibbous"
        elif mp < 15: phase_name = "Full Moon"
        elif mp < 21: phase_name = "Waning Gibbous"
        elif mp < 22: phase_name = "Last Quarter"
        else: phase_name = "Waning Crescent"
        phase_icons = {
            "New Moon": "🌑", "Waxing Crescent": "🌒", "First Quarter": "🌓",
            "Waxing Gibbous": "🌔", "Full Moon": "🌕", "Waning Gibbous": "🌖",
            "Last Quarter": "🌗", "Waning Crescent": "🌘"
        }
        return {
            "sunrise": s["sunrise"].strftime("%H:%M"),
            "sunset": s["sunset"].strftime("%H:%M"),
            "dawn": s["dawn"].strftime("%H:%M"),
            "dusk": s["dusk"].strftime("%H:%M"),
            "solar_noon": s["noon"].strftime("%H:%M"),
            "moon_phase": round(mp, 1),
            "moon_phase_name": phase_name,
            "moon_icon": phase_icons[phase_name]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/automation/rules")
def get_rules():
    try:
        conn = _db()
        rows = conn.execute(
            'SELECT id,name,category,enabled,trigger_type,last_triggered FROM automation_rules ORDER BY category,name'
        ).fetchall()
        conn.close()
        return {"rules": [{"id":r[0],"name":r[1],"category":r[2],"enabled":r[3],"trigger_type":r[4],"last_triggered":r[5]} for r in rows]}
    except Exception as e:
        return {"rules":[],"error":str(e)}

@app.post("/api/automation/rules")
def create_rule(rule: dict):
    try:
        import uuid
        rid = str(uuid.uuid4())[:8]
        now = int(_time.time())
        conn = _db()
        conn.execute(
            'INSERT INTO automation_rules (id,name,category,enabled,trigger_type,trigger_config,conditions,actions,created) VALUES (?,?,?,?,?,?,?,?,?)',
            (rid, rule['name'], rule.get('category','general'), rule.get('enabled',1),
             rule['trigger_type'], json.dumps(rule.get('trigger_config',{})),
             json.dumps(rule.get('conditions',[])), json.dumps(rule.get('actions',[])), now)
        )
        conn.commit()
        conn.close()
        return {"success":True,"id":rid}
    except Exception as e:
        return {"success":False,"error":str(e)}

@app.put("/api/automation/rules/{rule_id}")
def update_rule(rule_id: str, rule: dict):
    try:
        conn = _db()
        conn.execute(
            'UPDATE automation_rules SET name=?,category=?,enabled=?,trigger_type=?,trigger_config=?,conditions=?,actions=? WHERE id=?',
            (rule['name'], rule.get('category','general'), rule.get('enabled',1),
             rule['trigger_type'], json.dumps(rule.get('trigger_config',{})),
             json.dumps(rule.get('conditions',[])), json.dumps(rule.get('actions',[])), rule_id)
        )
        conn.commit()
        conn.close()
        return {"success":True}
    except Exception as e:
        return {"success":False,"error":str(e)}

@app.delete("/api/automation/rules/{rule_id}")
def delete_rule(rule_id: str):
    try:
        conn = _db()
        conn.execute('DELETE FROM automation_rules WHERE id=?', (rule_id,))
        conn.commit()
        conn.close()
        return {"success":True}
    except Exception as e:
        return {"success":False,"error":str(e)}

@app.post("/api/automation/rules/{rule_id}/trigger")
def manual_trigger(rule_id: str):
    try:
        conn = _db()
        row = conn.execute('SELECT name,actions FROM automation_rules WHERE id=?', (rule_id,)).fetchone()
        conn.close()
        if not row:
            return {"success":False,"error":"Rule not found"}
        actions = json.loads(row[1])
        for action in actions:
            if action.get('type') == 'light_control':
                requests.post(f'http://localhost:8000/api/lights/{action["device_id"]}/control', json=action.get('command',{}), timeout=5)
            elif action.get('type') == 'system_control':
                requests.post(f'http://localhost:8000/api/systems/{action["system_id"]}/control', json=action.get('command',{}), timeout=5)
        return {"success":True}
    except Exception as e:
        return {"success":False,"error":str(e)}

@app.get("/api/automation/log")
def get_automation_log(limit: int = 50):
    try:
        conn = _db()
        rows = conn.execute(
            'SELECT timestamp,rule_name,result,detail FROM automation_log ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        ).fetchall()
        conn.close()
        return {"log":[{"timestamp":r[0],"rule_name":r[1],"result":r[2],"detail":r[3]} for r in rows]}
    except Exception as e:
        return {"log":[],"error":str(e)}
