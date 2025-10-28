import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from api.games.entities.models import Entity
from api.games.entities.schemas import (
    EntityCreateRequest,
    EntityCreateResponse,
    EntityUpdateRequest,
    EntityUpdateResponse,
)

router = APIRouter()


@router.post("", response_model=EntityCreateResponse)
async def create_entity(
    scene_id: uuid.UUID,
    request: EntityCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    entity = Entity(
        name=request.name,
        scene_id=scene_id,
        entity_data=request.entity_data,
    )
    db.add(entity)
    await db.flush()
    return EntityCreateResponse(
        id=entity.id,
        scene_id=entity.scene_id,
        name=entity.name,
        entity_data=entity.entity_data,
    )


@router.put("/{entity_id}", response_model=EntityUpdateResponse)
async def update_entity(
    scene_id: uuid.UUID,
    entity_id: uuid.UUID,
    request: EntityUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    entity = await db.get(Entity, entity_id)
    if entity is None or entity.scene_id != scene_id:
        raise HTTPException(status_code=404, detail="Entity not found")

    entity.name = request.name
    entity.entity_data = request.entity_data

    await db.flush()
    return EntityUpdateResponse(
        id=entity.id,
        scene_id=entity.scene_id,
        name=entity.name,
        entity_data=entity.entity_data,
    )


@router.delete("/{entity_id}")
async def delete_entity(
    scene_id: uuid.UUID,
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    entity = await db.get(Entity, entity_id)
    if entity is None or entity.scene_id != scene_id:
        raise HTTPException(status_code=404, detail="Entity not found")
    await db.delete(entity)
    return {"id": entity.id}
