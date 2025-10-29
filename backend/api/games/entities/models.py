import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import NESEntity
from database import Base


class Entity(UUIDMixin, Base):
    __tablename__ = "entities"
    __table_args__ = (UniqueConstraint("game_id", "name", name="uq_entity_game_name"),)

    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_data: Mapped[NESEntity] = mapped_column(PydanticType(NESEntity), nullable=False)

    # Relationship to Game
    game: Mapped["Game"] = relationship("Game", back_populates="entities")  # type: ignore
