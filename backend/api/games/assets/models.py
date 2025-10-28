import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import AssetData, AssetType
from database import Base


class Asset(UUIDMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("game_id", "name", "type", name="uq_asset_game_name_type"),)

    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[AssetType] = mapped_column(nullable=False)
    data: Mapped[AssetData] = mapped_column(PydanticType(AssetData), nullable=False)

    game: Mapped["Game"] = relationship("Game", back_populates="assets", lazy="raise")  # type: ignore
