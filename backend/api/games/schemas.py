import uuid

from pydantic import BaseModel

from api.games.assets.schemas import AssetResponse
from api.games.entities.schemas import EntityResponse
from api.games.scenes.schemas import SceneCreateResponse
from core.schemas import GameData


class GameCommon(BaseModel):
    name: str


class GameCreateRequest(GameCommon):
    game_data: GameData


class GameCreateResponse(GameCommon):
    id: uuid.UUID
    game_data: GameData


class GameUpdateRequest(BaseModel):
    name: str | None = None
    game_data: GameData | None = None


class GameUpdateResponse(GameCommon):
    id: uuid.UUID
    game_data: GameData


class GameListItem(GameCommon):
    id: uuid.UUID
    game_data: GameData


class GameGetResponse(GameCommon):
    id: uuid.UUID
    game_data: GameData
    scenes: list[SceneCreateResponse]
    assets: list[AssetResponse]
    entities: list[EntityResponse]


class GameDeleteResponse(BaseModel):
    id: uuid.UUID
