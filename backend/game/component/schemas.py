import uuid

from pydantic import BaseModel

from core.schemas import ComponentData, ComponentType


class ComponentCreateRequest(BaseModel):
    name: str
    type: ComponentType
    component_data: ComponentData


class ComponentCreateResponse(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    type: ComponentType
    component_data: ComponentData
