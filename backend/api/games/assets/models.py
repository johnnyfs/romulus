import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import GameAssetData, GameAssetType
from database import Base


class GameAsset(UUIDMixin, Base):
    __tablename__ = "game_assets"
    __table_args__ = (UniqueConstraint("game_id", "name", "type", name="uq_game_asset_game_name_type"),)

    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[GameAssetType] = mapped_column(nullable=False)
    data: Mapped[GameAssetData] = mapped_column(PydanticType(GameAssetData), nullable=False)

    game: Mapped["Game"] = relationship("Game", back_populates="game_assets", lazy="raise")  # type: ignore
