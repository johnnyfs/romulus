import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from game.component.models import Component
from game.component.schemas import ComponentCreateRequest, ComponentCreateResponse

router = APIRouter()


@router.post("", response_model=ComponentCreateResponse)
async def create_component(
    game_id: uuid.UUID,
    request: ComponentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    # Extract type from component_data to keep SQL column in sync
    component_type = request.component_data.type

    component = Component(
        name=request.name,
        type=component_type,
        game_id=game_id,
        component_data=request.component_data,
    )
    db.add(component)
    await db.flush()  # Flush to generate the UUID
    return ComponentCreateResponse(
        id=component.id,
        game_id=component.game_id,
        name=component.name,
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
