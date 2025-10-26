import uuid

from dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException
from game.component.models import Component
from game.component.schemas import ComponentCreateRequest, ComponentCreateResponse
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.post("", response_model=ComponentCreateResponse)
async def create_component(
    game_id: uuid.UUID,
    request: ComponentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    component = Component(
        name=request.name,
        type=request.type,
        component_data=request.component_data,
        game_id=game_id,
    )
    db.add(component)
    await db.flush()  # Flush to generate the UUID
    return ComponentCreateResponse(
        id=component.id,
        game_id=component.game_id,
        name=component.name,
        type=component.type,
        component_data=component.component_data,
    )


@router.delete("/{component_id}")
async def delete_component(
    game_id: uuid.UUID,
    component_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    component = await db.get(Component, component_id)
    if component is None or component.game_id != game_id:
        raise HTTPException(status_code=404, detail="Component not found")
    await db.delete(component)
    return {"id": component.id}
