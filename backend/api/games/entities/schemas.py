import uuid

from pydantic import BaseModel

from core.schemas import NESEntity


class EntityCreateRequest(BaseModel):
    name: str
    entity_data: NESEntity


class EntityCreateResponse(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    entity_data: NESEntity


class EntityUpdateRequest(BaseModel):
    name: str | None = None
    entity_data: NESEntity | None = None


class EntityUpdateResponse(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    entity_data: NESEntity


class EntityResponse(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    name: str
    entity_data: NESEntity
