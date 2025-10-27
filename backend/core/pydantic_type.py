from typing import Any

from pydantic import BaseModel, TypeAdapter
from sqlalchemy import JSON, TypeDecorator


class PydanticType(TypeDecorator):
    """Generic SQLAlchemy type that marshals JSON through a Pydantic model."""

    impl = JSON
    cache_ok = True

    def __init__(self, pydantic_type):
        super().__init__()
        self.pydantic_type = pydantic_type
        self.type_adapter = TypeAdapter(pydantic_type)

    def process_bind_param(self, value: Any, dialect) -> dict | None:
        """Convert Pydantic model to JSON dict for database."""
        if value is None:
            return None
        if isinstance(value, BaseModel):
            return value.model_dump()
        return value

    def process_result_value(self, value: dict | None, dialect) -> Any:
        """Convert JSON dict from database to Pydantic model."""
        if value is None:
            return None
        return self.type_adapter.validate_python(value)
