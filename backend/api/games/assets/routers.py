import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.games.assets.models import GameAsset
from api.games.assets.schemas import GameAssetCreateRequest, GameAssetResponse
from dependencies import get_db

router = APIRouter()


@router.post("", response_model=GameAssetResponse)
async def create_game_asset(
    game_id: uuid.UUID,
    request: GameAssetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a game asset.

    Game assets are final, ready-to-use game resources like palettes.
    They don't require upload - just provide the name, type, and data.
    """
    # Create game asset record
    game_asset = GameAsset(
        game_id=game_id,
        name=request.name,
        type=request.type,
        data=request.data,
    )
    db.add(game_asset)
    await db.flush()  # Flush to generate the UUID

    return GameAssetResponse(
        id=game_asset.id,
        game_id=game_asset.game_id,
        name=game_asset.name,
        type=game_asset.type,
        data=game_asset.data,
    )


@router.get("/{game_asset_id}", response_model=GameAssetResponse)
async def get_game_asset(
    game_id: uuid.UUID,
    game_asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a game asset by ID."""
    game_asset = await db.get(GameAsset, game_asset_id)
    if game_asset is None or game_asset.game_id != game_id:
        raise HTTPException(status_code=404, detail="Game asset not found")

    return GameAssetResponse(
        id=game_asset.id,
        game_id=game_asset.game_id,
        name=game_asset.name,
        type=game_asset.type,
        data=game_asset.data,
    )


@router.get("/", response_model=list[GameAssetResponse])
async def list_game_assets(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all game assets for a game."""
    result = await db.execute(select(GameAsset).where(GameAsset.game_id == game_id))
    game_assets = result.scalars().all()

    return [
        GameAssetResponse(
            id=asset.id,
            game_id=asset.game_id,
            name=asset.name,
            type=asset.type,
            data=asset.data,
        )
        for asset in game_assets
    ]


@router.delete("/{game_asset_id}")
async def delete_game_asset(
    game_id: uuid.UUID,
    game_asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a game asset."""
    game_asset = await db.get(GameAsset, game_asset_id)
    if game_asset is None or game_asset.game_id != game_id:
        raise HTTPException(status_code=404, detail="Game asset not found")

    # Delete from database
    await db.delete(game_asset)

    return {"id": game_asset.id}
