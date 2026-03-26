from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import psutil
import shutil
import os
import asyncio

from backend.app.database import init_db, get_db, log_sensor_reading, log_system_event

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    log_system_event("pi5", "Dashboard started")
    task = asyncio.create_task(system_logger())
    yield
    task.cancel()

app = FastAPI(title="Pi5 Dashboard", lifespan=lifespan)

static_path = os.path.join(os.path.dirname(__file__), "../../frontend/static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

async def system_logger():
    while True:
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            disk = shutil.disk_usage("/")
            storage = round((disk.used / disk.total) * 100, 1)
            temps = psutil.sensors_temperatures()
            cpu_temp = None
            if "cpu_thermal" in temps:
                cpu_temp = round(temps["cpu_thermal"][0].current, 1)
            log_sensor_reading("pi5", "cpu_percent", cpu)
            log_sensor_reading("pi5", "ram_percent", ram)
            log_sensor_reading("pi5", "storage_percent", storage)
            if cpu_temp is not None:
                log_sensor_reading("pi5", "cpu_temp", cpu_temp)
        except Exception as e:
            print(f"Logger error: {e}")
        await asyncio.sleep(60)

@app.get("/")
async def root():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "../../frontend/templates/index.html")
    )

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "pi5-dashboard"}

@app.get("/api/system")
async def system_stats():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = shutil.disk_usage("/")
    storage = round((disk.used / disk.total) * 100, 1)
    temps = psutil.sensors_temperatures()
    cpu_temp = None
    if "cpu_thermal" in temps:
        cpu_temp = round(temps["cpu_thermal"][0].current, 1)
    return {
        "cpu": cpu,
        "ram": ram,
        "storage": storage,
        "cpu_temp": cpu_temp,
        "hailo": 0
    }

@app.get("/api/sensors/{device_id}")
async def get_sensor_data(device_id: str, sensor_type: str = None, hours: int = 24):
    conn = get_db()
    if sensor_type:
        rows = conn.execute(
            "SELECT timestamp, sensor_type, value FROM sensor_readings WHERE device_id = ? AND sensor_type = ? AND timestamp > datetime('now', ?) ORDER BY timestamp DESC",
            (device_id, sensor_type, f"-{hours} hours")
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT timestamp, sensor_type, value FROM sensor_readings WHERE device_id = ? AND timestamp > datetime('now', ?) ORDER BY timestamp DESC",
            (device_id, f"-{hours} hours")
        ).fetchall()
    conn.close()
    return [{"timestamp": r["timestamp"], "sensor_type": r["sensor_type"], "value": r["value"]} for r in rows]
