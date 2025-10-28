import uuid

from pydantic import BaseModel

from core.schemas import NESEntity


class EntityCreateRequest(BaseModel):
    name: str
    entity_data: NESEntity


class EntityCreateResponse(BaseModel):
    id: uuid.UUID
    scene_id: uuid.UUID
    name: str
    entity_data: NESEntity


class EntityUpdateRequest(BaseModel):
    name: str
    entity_data: NESEntity


class EntityUpdateResponse(BaseModel):
    id: uuid.UUID
    scene_id: uuid.UUID
    name: str
    entity_data: NESEntity
