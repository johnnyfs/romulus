import uuid

from core.schemas import NESScene
from pydantic import BaseModel

class SceneCommon(BaseModel):
    game_id: uuid.UUID
    name: str
    scene_data: NESScene

class SceneCreateRequest(SceneCommon):
    pass

class SceneCreateResponse(SceneCommon):
    id: uuid.UUID

class SceneDeleteResponse(BaseModel):
    id: uuid.UUID