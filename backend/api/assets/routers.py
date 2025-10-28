import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.assets.models import Asset
from api.assets.schemas import (
    AssetCreateRequest,
    AssetCreateResponse,
    AssetUpdateRequest,
    UploadTicketRequest,
    UploadTicketResponse,
)
from core.schemas import AssetType, ImageState
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
    - asset_id: The UUID that will be assigned to this asset
    """
    storage = get_storage_client()

    # Generate a unique asset ID
    asset_id = uuid.uuid4()

    # Generate storage key based on asset metadata and processing state
    storage_key = storage.generate_storage_key(request.filename, request.asset_data, asset_id)

    # Generate presigned upload URL
    upload_url = storage.get_presigned_upload_url(storage_key)

    return UploadTicketResponse(upload_url=upload_url, storage_key=storage_key, asset_id=asset_id)


@router.get("", response_model=list[AssetCreateResponse])
async def list_assets(
    asset_type: AssetType | None = Query(None, description="Filter by asset type"),
    state: ImageState | None = Query(None, description="Filter by image state (for image assets)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all assets with optional filtering.

    Query params:
    - asset_type: Filter by type (e.g., 'image')
    - state: Filter by processing state (e.g., 'raw', 'grouped', 'cleaned')
    """
    storage = get_storage_client()

    # Build query
    query = select(Asset)

    if asset_type:
        query = query.where(Asset.type == asset_type)

    # For state filtering, we need to filter on the JSONB column
    if state and asset_type == AssetType.IMAGE:
        query = query.where(Asset.asset_data['state'].astext == state.value)

    # Order by processed flag (unprocessed first), then by id (oldest first)
    query = query.order_by(
        Asset.asset_data['processed'].astext.asc(),  # unprocessed first (false < true)
        Asset.id.asc()
    )

    result = await db.execute(query)
    assets = result.scalars().all()

    # Generate download URLs for all assets
    response_list = []
    for asset in assets:
        download_url = storage.get_download_url(asset.storage_key)
        response_list.append(
            AssetCreateResponse(
                id=asset.id,
                storage_key=asset.storage_key,
                asset_data=asset.asset_data,
                download_url=download_url,
            )
        )

    return response_list


@router.post("", response_model=AssetCreateResponse)
async def create_asset(
    request: AssetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Finalize an asset upload with metadata.

    After the client has uploaded to the presigned URL, they should call this
    endpoint with the storage_key and asset metadata to finalize the upload.
    This will:
    1. Verify the file exists in storage
    2. Create the database record
    3. Write metadata.json to storage for recovery
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

    # Write metadata.json to storage for recovery
    metadata = {
        "id": str(asset.id),
        "type": asset.type.value,
        "storage_key": asset.storage_key,
        "asset_data": asset.asset_data.model_dump(mode='json'),
        "created_at": asset.created_at.isoformat() if hasattr(asset, 'created_at') else None,
    }
    storage.write_metadata(asset.storage_key, metadata)

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


@router.put("/{asset_id}", response_model=AssetCreateResponse)
async def update_asset(
    asset_id: uuid.UUID,
    request: AssetUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an asset's metadata.

    Typical use: Mark a raw asset as processed=true after creating grouped versions.
    Updates both the database record and the metadata.json file in storage.
    """
    asset = await db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Update asset data
    asset.asset_data = request.asset_data
    asset.type = request.asset_data.type  # Keep SQL column in sync

    await db.flush()
    await db.commit()

    # Update metadata.json in storage
    storage = get_storage_client()
    metadata = {
        "id": str(asset.id),
        "type": asset.type.value,
        "storage_key": asset.storage_key,
        "asset_data": asset.asset_data.model_dump(mode='json'),
        "created_at": asset.created_at.isoformat() if hasattr(asset, 'created_at') else None,
    }
    storage.write_metadata(asset.storage_key, metadata)

    # Generate download URL for the response
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
