import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dependencies import get_db
from api.games.scenes.models import Scene
from api.games.scenes.schemas import (
    EntityResponse,
    SceneCreateRequest,
    SceneCreateResponse,
    SceneDeleteResponse,
    SceneUpdateRequest,
    SceneUpdateResponse,
)

router = APIRouter()


@router.post("", response_model=SceneCreateResponse)
async def create_scene(
    game_id: uuid.UUID,
    request: SceneCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    scene = Scene(name=request.name, game_id=game_id, scene_data=request.scene_data)
    db.add(scene)
    await db.flush()  # Flush to generate the UUID
    return SceneCreateResponse(id=scene.id, game_id=scene.game_id, name=scene.name, scene_data=scene.scene_data)


@router.delete("/{scene_id}", response_model=SceneDeleteResponse)
async def delete_scene(
    game_id: uuid.UUID,
    scene_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    scene = await db.get(Scene, scene_id)
    if scene is None or scene.game_id != game_id:
        raise HTTPException(status_code=404, detail="Scene not found")
    await db.delete(scene)
    return SceneDeleteResponse(id=scene.id)


@router.put("/{scene_id}", response_model=SceneUpdateResponse)
async def update_scene(
    game_id: uuid.UUID,
    scene_id: uuid.UUID,
    request: SceneUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    # Load scene with entities
    stmt = select(Scene).where(Scene.id == scene_id).options(selectinload(Scene.entities))
    result = await db.execute(stmt)
    scene = result.scalar_one_or_none()

    if scene is None or scene.game_id != game_id:
        raise HTTPException(status_code=404, detail="Scene not found")

    if request.name is not None:
        scene.name = request.name
    if request.scene_data is not None:
        scene.scene_data = request.scene_data

    await db.flush()

    # Convert entities to response format
    entities = [
        EntityResponse(
            id=entity.id,
            scene_id=entity.scene_id,
            name=entity.name,
            entity_data=entity.entity_data,
        )
        for entity in scene.entities
    ]

    return SceneUpdateResponse(
        id=scene.id,
        game_id=scene.game_id,
        name=scene.name,
        scene_data=scene.scene_data,
        entities=entities,
    )
