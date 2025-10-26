import uuid

from pydantic import BaseModel

from core.schemas import ComponentType


class ComponentCreateRequest(BaseModel):
    name: str
    type: ComponentType


class ComponentCreateResponse(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    type: ComponentType
