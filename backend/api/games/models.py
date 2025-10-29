from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import UUIDMixin
from database import Base


class Game(UUIDMixin, Base):
    __tablename__ = "games"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    scenes: Mapped[list["Scene"]] = relationship( # type: ignore
        "Scene", back_populates="game", cascade="all, delete-orphan", lazy="raise"
    )
    assets: Mapped[list["Asset"]] = relationship( # type: ignore
        "Asset", back_populates="game", cascade="all, delete-orphan", lazy="raise"
    )  # type: ignore
