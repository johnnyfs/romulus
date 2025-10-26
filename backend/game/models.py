from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import UUIDMixin
from database import Base


class Game(UUIDMixin, Base):
    __tablename__ = "games"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationship to Scenes
    scenes: Mapped[list["Scene"]] = relationship("Scene", back_populates="game", cascade="all, delete-orphan", lazy="raise")