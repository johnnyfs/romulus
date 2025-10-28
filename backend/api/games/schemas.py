import uuid

from pydantic import BaseModel

from api.games.scenes.schemas import SceneCreateResponse
from api.games.components.schemas import ComponentCreateResponse
from api.games.assets.schemas import AssetResponse


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
    components: list[ComponentCreateResponse]
    assets: list[AssetResponse]


class GameDeleteResponse(BaseModel):
    id: uuid.UUID
