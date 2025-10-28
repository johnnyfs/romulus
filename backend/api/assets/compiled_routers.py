import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.assets.compiled_models import CompiledAsset
from api.assets.schemas import CompiledAssetCreateRequest, CompiledAssetResponse
from dependencies import get_db

router = APIRouter()


@router.post("", response_model=CompiledAssetResponse)
async def create_compiled_asset(
    request: CompiledAssetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a compiled asset.

    Compiled assets are final, ready-to-use game resources like palettes.
    They don't require upload - just provide the name, type, and data.
    """
    # Create compiled asset record
    compiled_asset = CompiledAsset(
        name=request.name,
        type=request.type,
        data=request.data,
    )
    db.add(compiled_asset)
    await db.flush()  # Flush to generate the UUID

    return CompiledAssetResponse(
        id=compiled_asset.id,
        name=compiled_asset.name,
        type=compiled_asset.type,
        data=compiled_asset.data,
    )


@router.get("/{compiled_asset_id}", response_model=CompiledAssetResponse)
async def get_compiled_asset(
    compiled_asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a compiled asset by ID."""
    compiled_asset = await db.get(CompiledAsset, compiled_asset_id)
    if compiled_asset is None:
        raise HTTPException(status_code=404, detail="Compiled asset not found")

    return CompiledAssetResponse(
        id=compiled_asset.id,
        name=compiled_asset.name,
        type=compiled_asset.type,
        data=compiled_asset.data,
    )


@router.get("/", response_model=list[CompiledAssetResponse])
async def list_compiled_assets(
    db: AsyncSession = Depends(get_db),
):
    """List all compiled assets."""
    result = await db.execute(select(CompiledAsset))
    compiled_assets = result.scalars().all()

    return [
        CompiledAssetResponse(
            id=asset.id,
            name=asset.name,
            type=asset.type,
            data=asset.data,
        )
        for asset in compiled_assets
    ]


@router.delete("/{compiled_asset_id}")
async def delete_compiled_asset(
    compiled_asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a compiled asset."""
    compiled_asset = await db.get(CompiledAsset, compiled_asset_id)
    if compiled_asset is None:
        raise HTTPException(status_code=404, detail="Compiled asset not found")

    # Delete from database
    await db.delete(compiled_asset)

    return {"id": compiled_asset.id}
