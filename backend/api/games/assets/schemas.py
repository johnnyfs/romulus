import uuid

from pydantic import BaseModel

from core.schemas import GameAssetData, GameAssetType


class GameAssetCreateRequest(BaseModel):
    """Request to create a game asset."""

    name: str
    type: GameAssetType
    data: GameAssetData


class GameAssetResponse(BaseModel):
    """Response for a game asset."""

    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    type: GameAssetType
    data: GameAssetData
