import uuid

from pydantic import BaseModel

from core.schemas import AssetData, AssetType


class AssetCreateRequest(BaseModel):
    """Request to create an asset."""

    name: str
    type: AssetType
    data: AssetData


class AssetResponse(BaseModel):
    """Response for an asset."""

    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    type: AssetType
    data: AssetData
