from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.games.routers import router as game_router
from api.games.scenes.routers import router as scene_router
from api.games.components.routers import router as component_router
from config import settings

v1_app = FastAPI()

# Register routers
v1_app.include_router(game_router, prefix="/games", tags=["games"])
v1_app.include_router(scene_router, prefix="/games/{game_id}/scenes", tags=["scenes"])
v1_app.include_router(component_router, prefix="/games/{game_id}/components", tags=["components"])

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{settings.FRONTEND_URL}"],
    allow_methods=["*"],
)

app.mount("/api/v1", v1_app)