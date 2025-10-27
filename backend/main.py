from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import settings
from game.component.routers import router as component_router
from game.routers import router as game_router
from game.scene.routers import router as scene_router
from admin.assets import router as admin_assets_router

app = FastAPI()

# Mount static files for assets (development only)
REPO_ROOT = Path(__file__).parent.parent
ASSETS_DIR = REPO_ROOT / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Configure CORS - allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register routers
app.include_router(game_router, prefix="/api/v1/games", tags=["games"])
app.include_router(scene_router, prefix="/api/v1/games/{game_id}/scenes", tags=["scenes"])
app.include_router(component_router, prefix="/api/v1/games/{game_id}/components", tags=["components"])

# Admin routers (development only)
app.include_router(admin_assets_router)
