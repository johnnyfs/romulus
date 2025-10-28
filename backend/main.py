import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.assets.routers import router as asset_router
from api.games.routers import router as game_router
from api.games.scenes.routers import router as scene_router
from api.games.entities.routers import router as entity_router
from api.games.components.routers import router as component_router
from config import settings

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_level_value = getattr(logging, log_level, logging.INFO)

logging.basicConfig(
    level=log_level_value,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Set root logger level explicitly (this will cascade to all child loggers)
logging.getLogger().setLevel(log_level_value)

logger = logging.getLogger(__name__)
logger.info(f"Logging configured at {log_level} level")

v1_app = FastAPI()

# Register routers
v1_app.include_router(asset_router, prefix="/assets", tags=["assets"])
v1_app.include_router(game_router, prefix="/games", tags=["games"])
v1_app.include_router(scene_router, prefix="/games/{game_id}/scenes", tags=["scenes"])
v1_app.include_router(entity_router, prefix="/games/{game_id}/scenes/{scene_id}/entities", tags=["entities"])
v1_app.include_router(component_router, prefix="/games/{game_id}/components", tags=["components"])

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{settings.FRONTEND_URL}"],
    allow_methods=["*"],
)

app.mount("/api/v1", v1_app)