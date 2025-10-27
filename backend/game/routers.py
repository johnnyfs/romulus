import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.rom.builder import RomBuilder
from core.rom.registry import CodeBlockRegistry
from core.rom.rom import Rom
from core.schemas import NESColor, NESScene
from dependencies import get_db
from game.models import Game
from game.scene.models import Scene
from game.scene.routers import router as scene_router
from game.scene.schemas import SceneCreateResponse
from game.schemas import GameCreateRequest, GameCreateResponse, GameDeleteResponse, GameGetResponse, GameListItem

router = APIRouter()
router.include_router(scene_router, prefix="/{game_id}/scenes", tags=["scenes"])


@router.get("", response_model=list[GameListItem])
async def list_games(
    db: AsyncSession = Depends(get_db),
):
    # Query all games
    stmt = select(Game)

    result = await db.execute(stmt)

    games = result.scalars().all()

    return [GameListItem(id=game.id, name=game.name) for game in games]


@router.post("", response_model=GameCreateResponse)
async def create_game(
    request: GameCreateRequest,
    default_: bool = Query(False, alias="default"),
    db: AsyncSession = Depends(get_db),
):
    game = Game(name=request.name)

    if default_:
        # Default game has a single scene called main, dark blue background, no palettes.
        scene_data = NESScene(background_color=NESColor(index=0x02))
        scene = Scene(name="main", game_id=game.id, scene_data=scene_data)
        game.scenes.append(scene)

    db.add(game)
    await db.flush()  # Flush to generate the UUID
    return GameCreateResponse(id=game.id, name=game.name)


@router.get("/{game_id}", response_model=GameGetResponse)
async def get_game(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    # Query game with scenes eagerly loaded
    stmt = select(Game).where(Game.id == game_id).options(selectinload(Game.scenes))
    result = await db.execute(stmt)
    game = result.scalar_one_or_none()

    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    # Convert scenes to response format
    scenes = [
        SceneCreateResponse(id=scene.id, game_id=scene.game_id, name=scene.name, scene_data=scene.scene_data)
        for scene in game.scenes
    ]

    return GameGetResponse(id=game.id, name=game.name, scenes=scenes)


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


@router.post("/{game_id}/render")
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
