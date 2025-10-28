import uuid

from pydantic import BaseModel

from core.schemas import ComponentData


class ComponentCreateRequest(BaseModel):
    name: str
    component_data: ComponentData


class ComponentCreateResponse(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    component_data: ComponentData


class ComponentUpdateRequest(BaseModel):
    name: str
    component_data: ComponentData


class ComponentUpdateResponse(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    component_data: ComponentData
