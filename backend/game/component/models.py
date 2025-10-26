import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base, UUIDMixin
from core.schemas import ComponentType


class Component(UUIDMixin, Base):
    __tablename__ = "components"
    __table_args__ = (
        UniqueConstraint("game_id", "name", "type", name="uq_component_game_name_type"),
    )

    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[ComponentType] = mapped_column(nullable=False)

    game: Mapped["Game"] = relationship("Game", back_populates="components", lazy="raise")
