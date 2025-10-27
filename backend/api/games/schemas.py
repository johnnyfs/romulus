import uuid

from pydantic import BaseModel

from api.games.scenes.schemas import SceneCreateResponse


class GameCommon(BaseModel):
    name: str


class GameCreateRequest(GameCommon):
    pass


class GameCreateResponse(GameCommon):
    id: uuid.UUID


class GameListItem(GameCommon):
    id: uuid.UUID


class GameGetResponse(GameCommon):
    id: uuid.UUID
    scenes: list[SceneCreateResponse]


class GameDeleteResponse(BaseModel):
    id: uuid.UUID
