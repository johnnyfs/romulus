from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.models import UUIDMixin
from core.pydantic_type import PydanticType
from core.schemas import CompiledAssetData, CompiledAssetType
from database import Base


class CompiledAsset(UUIDMixin, Base):
    __tablename__ = "compiled_assets"
    __table_args__ = (UniqueConstraint("name", "type", name="uq_compiled_asset_name_type"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[CompiledAssetType] = mapped_column(nullable=False)
    data: Mapped[CompiledAssetData] = mapped_column(PydanticType(CompiledAssetData), nullable=False)
