import uuid

from pydantic import BaseModel

from core.schemas import NESScene, NESEntity


class EntityResponse(BaseModel):
    id: uuid.UUID
    scene_id: uuid.UUID
    name: str
    entity_data: NESEntity


class SceneCommon(BaseModel):
    game_id: uuid.UUID
    name: str
    scene_data: NESScene


class SceneCreateRequest(SceneCommon):
    pass


class SceneCreateResponse(SceneCommon):
    id: uuid.UUID
    entities: list[EntityResponse] = []


class SceneUpdateRequest(BaseModel):
    name: str | None = None
    scene_data: NESScene | None = None


class SceneUpdateResponse(SceneCommon):
    id: uuid.UUID
    entities: list[EntityResponse] = []


class SceneDeleteResponse(BaseModel):
    id: uuid.UUID
