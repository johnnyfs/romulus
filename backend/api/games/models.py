from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import GameData
from database import Base


class Game(UUIDMixin, Base):
    __tablename__ = "games"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    game_data: Mapped[GameData] = mapped_column(PydanticType(GameData), nullable=False)

    # Relationships
    scenes: Mapped[list["Scene"]] = relationship( # type: ignore
        "Scene", back_populates="game", cascade="all, delete-orphan", lazy="raise"
    )
    assets: Mapped[list["Asset"]] = relationship( # type: ignore
        "Asset", back_populates="game", cascade="all, delete-orphan", lazy="raise"
    )  # type: ignore
    entities: Mapped[list["Entity"]] = relationship( # type: ignore
        "Entity", back_populates="game", cascade="all, delete-orphan", lazy="raise"
    )  # type: ignore
