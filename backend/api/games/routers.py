import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.games.assets.models import Asset
from api.games.assets.schemas import AssetResponse
from api.games.entities.models import Entity
from api.games.entities.schemas import EntityResponse
from api.games.models import Game
from api.games.scenes.models import Scene
from api.games.scenes.schemas import SceneCreateResponse
from api.games.schemas import (
    GameCreateRequest,
    GameCreateResponse,
    GameDeleteResponse,
    GameGetResponse,
    GameListItem,
    GameUpdateRequest,
    GameUpdateResponse,
)
from core.rom.builder import RomBuilder
from core.rom.registry import CodeBlockRegistry
from core.rom.rom import Rom
from core.schemas import (
    AssetType,
    NESColor,
    NESSpriteSetAssetData,
    NESScene,
    SpriteSetType,
)
from dependencies import get_db

router = APIRouter()


@router.get("", response_model=list[GameListItem])
async def list_games(
    db: AsyncSession = Depends(get_db),
):
    # Query all games
    stmt = select(Game)

    result = await db.execute(stmt)

    games = result.scalars().all()

    return [GameListItem(id=game.id, name=game.name, game_data=game.game_data) for game in games]


@router.post("", response_model=GameCreateResponse)
async def create_game(
    request: GameCreateRequest,
    default_: bool = Query(False, alias="default"),
    db: AsyncSession = Depends(get_db),
):
    game = Game(name=request.name, game_data=request.game_data)

    if default_:
        # Default game has a single scene called main, dark blue background, no palettes.
        scene_data = NESScene(background_color=NESColor(index=0x02))
        scene = Scene(name="main", game_id=game.id, scene_data=scene_data)
        game.scenes.append(scene)

        # Add a dummy static spriteset for testing
        spriteset_data = NESSpriteSetAssetData(
            type=AssetType.SPRITE_SET,
            sprite_set_type=SpriteSetType.STATIC,
        )
        spriteset = Asset(
            name="Test Sprite",
            game_id=game.id,
            type=AssetType.SPRITE_SET,
            data=spriteset_data,
        )
        game.assets.append(spriteset)

    db.add(game)
    await db.flush()  # Flush to generate the UUID
    return GameCreateResponse(id=game.id, name=game.name, game_data=game.game_data)


@router.get("/{game_id}", response_model=GameGetResponse)
async def get_game(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    # Query game with scenes, entities, and assets eagerly loaded
    stmt = select(Game).where(Game.id == game_id).options(
        selectinload(Game.scenes),
        selectinload(Game.assets),
        selectinload(Game.entities)
    )
    result = await db.execute(stmt)
    game = result.scalar_one_or_none()

    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    # Convert scenes to response format
    scenes = [
        SceneCreateResponse(
            id=scene.id,
            game_id=scene.game_id,
            name=scene.name,
            scene_data=scene.scene_data,
        )
        for scene in game.scenes
    ]

    # Convert assets to response format
    assets = [
        AssetResponse(id=asset.id, game_id=asset.game_id, name=asset.name, type=asset.type, data=asset.data)
        for asset in game.assets
    ]

    # Convert entities to response format (components are embedded in entity_data)
    entities = [
        EntityResponse(
            id=entity.id,
            game_id=entity.game_id,
            name=entity.name,
            entity_data=entity.entity_data,
        )
        for entity in game.entities
    ]

    return GameGetResponse(
        id=game.id,
        name=game.name,
        game_data=game.game_data,
        scenes=scenes,
        assets=assets,
        entities=entities
    )


@router.put("/{game_id}", response_model=GameUpdateResponse)
async def update_game(
    game_id: uuid.UUID,
    request: GameUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    game = await db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    if request.name is not None:
        game.name = request.name
    if request.game_data is not None:
        game.game_data = request.game_data

    await db.flush()
    return GameUpdateResponse(id=game.id, name=game.name, game_data=game.game_data)


@router.delete("/{game_id}", response_model=GameDeleteResponse)
async def delete_game(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    game = await db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    await db.delete(game)
    return GameDeleteResponse(id=game.id)


@router.post(
    "/{game_id}/render",
    response_class=Response,
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "NES ROM binary data",
        }
    },
)
async def render_game(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Renders a game into a NES ROM file.

    Returns the ROM data as application/octet-stream which can be
    loaded directly into a NES emulator.
    """
    # Build and render the ROM
    rom = Rom()
    registry = CodeBlockRegistry()
    builder = RomBuilder(db=db, rom=rom, registry=registry)

    try:
        rom_bytes = await builder.build(game_id=game_id, initial_scene_name="main")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing dependency: {str(e)}")

    # Return as binary data with appropriate content type
    return Response(
        content=rom_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="game_{game_id}.nes"'},
    )
