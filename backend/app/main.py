from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Pi5 Dashboard")

# Serve static files (CSS, JS)
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
