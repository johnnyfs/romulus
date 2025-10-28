import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.assets.models import Asset
from api.assets.schemas import (
    AssetCreateRequest,
    AssetCreateResponse,
    UploadTicketRequest,
    UploadTicketResponse,
)
from core.storage import get_storage_client
from dependencies import get_db

router = APIRouter()


@router.post("/upload", response_model=UploadTicketResponse)
async def get_upload_ticket(request: UploadTicketRequest):
    """
    Get a presigned URL for uploading an asset.

    Returns an upload ticket containing:
    - upload_url: Presigned URL where the client should PUT the file
    - storage_key: Key to reference this upload when finalizing
    """
    storage = get_storage_client()

    # Generate a unique storage key for this file
    storage_key = storage.generate_storage_key(request.filename)

    # Generate presigned upload URL
    upload_url = storage.get_presigned_upload_url(storage_key)

    return UploadTicketResponse(upload_url=upload_url, storage_key=storage_key)


@router.post("", response_model=AssetCreateResponse)
async def create_asset(
    request: AssetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Finalize an asset upload with metadata.

    After the client has uploaded to the presigned URL, they should call this
    endpoint with the storage_key and asset metadata to finalize the upload.
    """
    storage = get_storage_client()

    # Verify the object exists in storage
    if not storage.object_exists(request.storage_key):
        raise HTTPException(status_code=400, detail="Asset not found in storage. Upload may have failed.")

    # Extract type from asset_data to keep SQL column in sync
    asset_type = request.asset_data.type

    # Create asset record
    asset = Asset(
        type=asset_type,
        storage_key=request.storage_key,
        asset_data=request.asset_data,
    )
    db.add(asset)
    await db.flush()  # Flush to generate the UUID

    # Generate download URL for the response
    download_url = storage.get_download_url(asset.storage_key)

    return AssetCreateResponse(
        id=asset.id,
        storage_key=asset.storage_key,
        asset_data=asset.asset_data,
        download_url=download_url,
    )


@router.get("/{asset_id}", response_model=AssetCreateResponse)
async def get_asset(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get an asset by ID."""
    asset = await db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Generate download URL for the response
    storage = get_storage_client()
    download_url = storage.get_download_url(asset.storage_key)

    return AssetCreateResponse(
        id=asset.id,
        storage_key=asset.storage_key,
        asset_data=asset.asset_data,
        download_url=download_url,
    )


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an asset and its stored file."""
    asset = await db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Delete from storage
    storage = get_storage_client()
    try:
        storage.delete_object(asset.storage_key)
    except Exception:
        # Log but don't fail if storage deletion fails
        pass

    # Delete from database
    await db.delete(asset)

    return {"id": asset.id}
