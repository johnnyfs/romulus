import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import NESEntity
from database import Base


class Entity(UUIDMixin, Base):
    __tablename__ = "entities"
    __table_args__ = (UniqueConstraint("scene_id", "name", name="uq_entity_scene_name"),)

    scene_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scenes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_data: Mapped[NESEntity] = mapped_column(PydanticType(NESEntity), nullable=False)

    # Relationship to Scene
    scene: Mapped["Scene"] = relationship("Scene", back_populates="entities")  # type: ignore
