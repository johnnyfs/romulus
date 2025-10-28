from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import AssetData, AssetType
from database import Base


class Asset(UUIDMixin, Base):
    __tablename__ = "assets"

    type: Mapped[AssetType] = mapped_column(nullable=False, index=True)
    asset_data: Mapped[AssetData] = mapped_column(PydanticType(AssetData), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
