import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.games.assets.models import Asset
from api.games.assets.schemas import AssetCreateRequest, AssetResponse
from dependencies import get_db

router = APIRouter()


@router.post("", response_model=AssetResponse)
async def create_asset(
    game_id: uuid.UUID,
    request: AssetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a game asset.

    Game assets are final, ready-to-use game resources like palettes.
    They don't require upload - just provide the name, type, and data.
    """
    # Create game asset record
    asset = Asset(
        game_id=game_id,
        name=request.name,
        type=request.type,
        data=request.data,
    )
    db.add(asset)
    await db.flush()  # Flush to generate the UUID

    return AssetResponse(
        id=asset.id,
        game_id=asset.game_id,
        name=asset.name,
        type=asset.type,
        data=asset.data,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    game_id: uuid.UUID,
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a game asset by ID."""
    asset = await db.get(Asset, asset_id)
    if asset is None or asset.game_id != game_id:
        raise HTTPException(status_code=404, detail="Game asset not found")

    return AssetResponse(
        id=asset.id,
        game_id=asset.game_id,
        name=asset.name,
        type=asset.type,
        data=asset.data,
    )


@router.get("/", response_model=list[AssetResponse])
async def list_assets(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all game assets for a game."""
    result = await db.execute(select(Asset).where(Asset.game_id == game_id))
    assets = result.scalars().all()

    return [
        AssetResponse(
            id=asset.id,
            game_id=asset.game_id,
            name=asset.name,
            type=asset.type,
            data=asset.data,
        )
        for asset in assets
    ]


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    game_id: uuid.UUID,
    asset_id: uuid.UUID,
    request: AssetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update a game asset."""
    asset = await db.get(Asset, asset_id)
    if asset is None or asset.game_id != game_id:
        raise HTTPException(status_code=404, detail="Game asset not found")

    # Update asset fields
    asset.name = request.name
    asset.type = request.type
    asset.data = request.data

    await db.flush()

    return AssetResponse(
        id=asset.id,
        game_id=asset.game_id,
        name=asset.name,
        type=asset.type,
        data=asset.data,
    )


@router.delete("/{asset_id}")
async def delete_asset(
    game_id: uuid.UUID,
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a game asset."""
    asset = await db.get(Asset, asset_id)
    if asset is None or asset.game_id != game_id:
        raise HTTPException(status_code=404, detail="Game asset not found")

    # Delete from database
    await db.delete(asset)

    return {"id": asset.id}
