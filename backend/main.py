from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from game.component.routers import router as component_router
from game.routers import router as game_router
from game.scene.routers import router as scene_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(game_router, prefix="/api/v1/games", tags=["games"])
app.include_router(scene_router, prefix="/api/v1/games/{game_id}/scenes", tags=["scenes"])
app.include_router(component_router, prefix="/api/v1/games/{game_id}/components", tags=["components"])
