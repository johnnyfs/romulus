import uuid

from pydantic import BaseModel

from core.schemas import AssetData


class UploadTicketRequest(BaseModel):
    """Request to get a presigned upload URL."""

    filename: str
    asset_data: AssetData


class UploadTicketResponse(BaseModel):
    """Response containing presigned upload URL and storage key."""

    upload_url: str
    storage_key: str
    asset_id: uuid.UUID


class AssetCreateRequest(BaseModel):
    """Request to finalize an asset upload with metadata."""

    storage_key: str
    asset_data: AssetData


class AssetCreateResponse(BaseModel):
    """Response after creating an asset."""

    id: uuid.UUID
    storage_key: str
    asset_data: AssetData
    download_url: str
