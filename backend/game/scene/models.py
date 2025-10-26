import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import NESScene
from database import Base


class Scene(UUIDMixin, Base):
    __tablename__ = "scenes"

    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scene_data: Mapped[NESScene] = mapped_column(PydanticType(NESScene), nullable=False)

    # Relationship to Game
    game: Mapped["Game"] = relationship("Game", back_populates="scenes")
