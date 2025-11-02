import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.games.entities.models import Entity
from api.games.entities.schemas import (
    EntityCreateRequest,
    EntityCreateResponse,
    EntityUpdateRequest,
    EntityUpdateResponse,
)
from dependencies import get_db

router = APIRouter()


@router.post("", response_model=EntityCreateResponse)
async def create_entity(
    game_id: uuid.UUID,
    request: EntityCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    entity = Entity(
        name=request.name,
        game_id=game_id,
        entity_data=request.entity_data,
    )
    db.add(entity)
    await db.flush()
    await db.refresh(entity, attribute_names=["components"])
    return EntityCreateResponse(
        id=entity.id,
        game_id=entity.game_id,
        name=entity.name,
        entity_data=entity.entity_data,
        components=[c.component_data for c in entity.components],
    )


@router.put("/{entity_id}", response_model=EntityUpdateResponse)
async def update_entity(
    game_id: uuid.UUID,
    entity_id: uuid.UUID,
    request: EntityUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Entity).where(Entity.id == entity_id).options(selectinload(Entity.components))
    result = await db.execute(stmt)
    entity = result.scalar_one_or_none()

    if entity is None or entity.game_id != game_id:
        raise HTTPException(status_code=404, detail="Entity not found")

    if request.name is not None:
        entity.name = request.name
    if request.entity_data is not None:
        entity.entity_data = request.entity_data

    await db.flush()
    return EntityUpdateResponse(
        id=entity.id,
        game_id=entity.game_id,
        name=entity.name,
        entity_data=entity.entity_data,
        components=[c.component_data for c in entity.components],
    )


@router.delete("/{entity_id}")
async def delete_entity(
    game_id: uuid.UUID,
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    entity = await db.get(Entity, entity_id)
    if entity is None or entity.game_id != game_id:
        raise HTTPException(status_code=404, detail="Entity not found")
    await db.delete(entity)
    return {"id": entity.id}
