from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import psutil
import shutil
import os

app = FastAPI(title="Pi5 Dashboard")

static_path = os.path.join(os.path.dirname(__file__), "../../frontend/static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

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
