import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.resources.models import Resource
from api.resources.schemas import (
    ResourceCreateRequest,
    ResourceCreateResponse,
    ResourceUpdateRequest,
    UploadTicketRequest,
    UploadTicketResponse,
)
from core.schemas import ImageState, ResourceType
from core.storage import get_storage_client
from dependencies import get_db

router = APIRouter()


@router.post("/upload", response_model=UploadTicketResponse)
async def get_upload_ticket(request: UploadTicketRequest):
    """
    Get a presigned URL for uploading an resource.

    Returns an upload ticket containing:
    - upload_url: Presigned URL where the client should PUT the file
    - storage_key: Key to reference this upload when finalizing
    - resource_id: The UUID that will be assigned to this resource
    """
    storage = get_storage_client()

    # Generate a unique resource ID
    resource_id = uuid.uuid4()

    # Generate storage key based on resource metadata and processing state
    storage_key = storage.generate_storage_key(request.filename, request.resource_data, resource_id)

    # Generate presigned upload URL
    upload_url = storage.get_presigned_upload_url(storage_key)

    return UploadTicketResponse(upload_url=upload_url, storage_key=storage_key, resource_id=resource_id)


@router.get("", response_model=list[ResourceCreateResponse])
async def list_resources(
    resource_type: ResourceType | None = Query(None, description="Filter by resource type"),
    state: ImageState | None = Query(None, description="Filter by image state (for image resources)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all resources with optional filtering.

    Query params:
    - resource_type: Filter by type (e.g., 'image')
    - state: Filter by processing state (e.g., 'raw', 'grouped', 'cleaned')
    """
    storage = get_storage_client()

    # Build query
    query = select(Resource)

    if resource_type:
        query = query.where(Resource.type == resource_type)

    # For state filtering, we need to filter on the JSONB column
    # Access the column directly from the table
    resource_data_col = Resource.__table__.c.resource_data
    if state and resource_type == ResourceType.IMAGE:
        query = query.where(cast(resource_data_col['state'], String) == state.value)

    # Order by processed flag (unprocessed first), then by id (oldest first)
    query = query.order_by(
        cast(resource_data_col['processed'], String).asc(),  # unprocessed first (false < true)
        Resource.id.asc()
    )

    result = await db.execute(query)
    resources = result.scalars().all()

    # Generate download URLs for all resources
    response_list = []
    for resource in resources:
        download_url = storage.get_download_url(resource.storage_key)
        response_list.append(
            ResourceCreateResponse(
                id=resource.id,
                storage_key=resource.storage_key,
                resource_data=resource.resource_data,
                download_url=download_url,
            )
        )

    return response_list


@router.post("", response_model=ResourceCreateResponse)
async def create_resource(
    request: ResourceCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Finalize an resource upload with metadata.

    After the client has uploaded to the presigned URL, they should call this
    endpoint with the storage_key and resource metadata to finalize the upload.
    This will:
    1. Verify the file exists in storage
    2. Create the database record
    3. Write metadata.json to storage for recovery
    """
    storage = get_storage_client()

    # Verify the object exists in storage
    if not storage.object_exists(request.storage_key):
        raise HTTPException(status_code=400, detail="Resource not found in storage. Upload may have failed.")

    # Extract type from resource_data to keep SQL column in sync
    resource_type = request.resource_data.type

    # Create resource record
    resource = Resource(
        type=resource_type,
        storage_key=request.storage_key,
        resource_data=request.resource_data,
    )
    db.add(resource)
    await db.flush()  # Flush to generate the UUID

    # Write metadata.json to storage for recovery
    metadata = {
        "id": str(resource.id),
        "type": resource.type.value,
        "storage_key": resource.storage_key,
        "resource_data": resource.resource_data.model_dump(mode='json'),
        "created_at": resource.created_at.isoformat() if hasattr(resource, 'created_at') else None,
    }
    storage.write_metadata(resource.storage_key, metadata)

    # Generate download URL for the response
    download_url = storage.get_download_url(resource.storage_key)

    return ResourceCreateResponse(
        id=resource.id,
        storage_key=resource.storage_key,
        resource_data=resource.resource_data,
        download_url=download_url,
    )


@router.get("/{resource_id}", response_model=ResourceCreateResponse)
async def get_resource(
    resource_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get an resource by ID."""
    resource = await db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Generate download URL for the response
    storage = get_storage_client()
    download_url = storage.get_download_url(resource.storage_key)

    return ResourceCreateResponse(
        id=resource.id,
        storage_key=resource.storage_key,
        resource_data=resource.resource_data,
        download_url=download_url,
    )


@router.put("/{resource_id}", response_model=ResourceCreateResponse)
async def update_resource(
    resource_id: uuid.UUID,
    request: ResourceUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an resource's metadata.

    Typical use: Mark a raw resource as processed=true after creating grouped versions.
    Updates both the database record and the metadata.json file in storage.
    """
    resource = await db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Update resource data
    resource.resource_data = request.resource_data
    resource.type = request.resource_data.type  # Keep SQL column in sync

    await db.flush()
    await db.commit()

    # Update metadata.json in storage
    storage = get_storage_client()
    metadata = {
        "id": str(resource.id),
        "type": resource.type.value,
        "storage_key": resource.storage_key,
        "resource_data": resource.resource_data.model_dump(mode='json'),
        "created_at": resource.created_at.isoformat() if hasattr(resource, 'created_at') else None,
    }
    storage.write_metadata(resource.storage_key, metadata)

    # Generate download URL for the response
    download_url = storage.get_download_url(resource.storage_key)

    return ResourceCreateResponse(
        id=resource.id,
        storage_key=resource.storage_key,
        resource_data=resource.resource_data,
        download_url=download_url,
    )


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an resource and its stored file."""
    resource = await db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Delete from storage
    storage = get_storage_client()
    try:
        storage.delete_object(resource.storage_key)
    except Exception:
        # Log but don't fail if storage deletion fails
        pass

    # Delete from database
    await db.delete(resource)

    return {"id": resource.id}
