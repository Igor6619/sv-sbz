import uuid
from typing import Optional
from pydantic import BaseModel, Field
from ..tools.pydantic import PydanticHelper


class TagModel(BaseModel, PydanticHelper.mixins.uuid("id")):
    """Модель тега"""

    id: uuid.UUID = Field(
        ...,
        description="Уникальный идентификатор тега",
    )

    name: str = Field(
        ...,
        description="Наименование тега",
    )


class TagSchema(BaseModel, PydanticHelper.mixins.uuid("id")):
    """Модель тега"""

    id: uuid.UUID = Field(
        description="Уникальный идентификатор тега",
    )

    name: Optional[str] = Field(
        default=None,
        description="Наименование тега",
    )


__all__ = ["TagModel", "TagSchema"]
