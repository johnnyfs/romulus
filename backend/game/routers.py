import uuid
from fastapi import APIRouter, Depends
from game.models import Game
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from game.schemas import GameCreateRequest, GameCreateResponse, GameDeleteResponse, GameGetResponse, GameListItem

from game.scene.routers import router as scene_router

router = APIRouter()
router.include_router(scene_router, prefix="/{game_id}/scenes", tags=["scenes"])

@router.get("", response_model=list[GameListItem])
async def list_games(
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select

    # Query all games
    stmt = select(Game)
    result = await db.execute(stmt)
    games = result.scalars().all()

    return [GameListItem(id=game.id, name=game.name) for game in games]

@router.post("", response_model=GameCreateResponse)
async def create_game(
    request: GameCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    game = Game(name=request.name)
    db.add(game)
    await db.flush()  # Flush to generate the UUID
    return GameCreateResponse(id=game.id, name=game.name)

@router.get("/{game_id}", response_model=GameGetResponse)
async def get_game(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from game.scene.schemas import SceneCreateResponse

    # Query game with scenes eagerly loaded
    stmt = select(Game).where(Game.id == game_id).options(selectinload(Game.scenes))
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
            scene_data=scene.scene_data
        )
        for scene in game.scenes
    ]

    return GameGetResponse(id=game.id, name=game.name, scenes=scenes)

@router.delete("/{game_id}", response_model=GameDeleteResponse)
async def delete_game(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException

    game = await db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    await db.delete(game)
    return GameDeleteResponse(id=game.id)
