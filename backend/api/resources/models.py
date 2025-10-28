from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import ResourceData, ResourceType
from database import Base


class Resource(UUIDMixin, Base):
    __tablename__ = "resources"

    type: Mapped[ResourceType] = mapped_column(nullable=False, index=True)
    resource_data: Mapped[ResourceData] = mapped_column(PydanticType(ResourceData), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
