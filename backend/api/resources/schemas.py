import uuid

from pydantic import BaseModel

from core.schemas import ResourceData


class UploadTicketRequest(BaseModel):
    """Request to get a presigned upload URL."""

    filename: str
    resource_data: ResourceData


class UploadTicketResponse(BaseModel):
    """Response containing presigned upload URL and storage key."""

    upload_url: str
    storage_key: str
    resource_id: uuid.UUID


class ResourceCreateRequest(BaseModel):
    """Request to finalize a resource upload with metadata."""

    storage_key: str
    resource_data: ResourceData


class ResourceCreateResponse(BaseModel):
    """Response after creating a resource."""

    id: uuid.UUID
    storage_key: str
    resource_data: ResourceData
    download_url: str


class ResourceUpdateRequest(BaseModel):
    """Request to update a resource's metadata."""

    resource_data: ResourceData
