from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from ....service import UserModel, PydanticHelper


class BaseModelMixin(
    BaseModel,
    PydanticHelper.mixins.uuid("id"),
    PydanticHelper.mixins.datetime("created", "modified", "deleted"),
):
    """Миксин с базовыми полями модели"""

    id: UUID = Field(
        ...,
        description="Идентификатор",
    )

    created: datetime = Field(
        ...,
        description="Время создания",
    )

    modified: datetime = Field(
        ...,
        description="Время последнего изменения",
    )

    deleted: Optional[datetime] = Field(
        default=None,
        description="Время удаления",
    )

    enabled: bool = Field(
        ...,
        description="False - ресурс удален",
    )


class AuthorModel(BaseModelMixin):
    """Модель автора"""

    name: str = Field(
        ...,
        description="Наименование",
    )


class FileTagModel(BaseModelMixin):
    """Модель тега"""

    name: str = Field(
        ...,
        description="Наименование",
    )

    code: Optional[str] = Field(
        default=None,
        description="Код",
    )

    keyword: bool = Field(
        ...,
        description="Является ли ключевым словом",
    )

    children: list["FileTagModel"] = Field(
        default_factory=list["FileTagModel"],
        description="Список дочерних тегов",
    )

    @field_validator("children", mode="before")
    @classmethod
    def children_validator(cls, value: list["FileTagModel"]) -> list["FileTagModel"]:
        if value is None:
            value = list()
        return value


class FileTypeModel(BaseModelMixin):
    """Представление типа файла"""

    name: str = Field(
        ...,
        description="Наименование",
    )

    code: Optional[str] = Field(
        default=None,
        description="Код",
    )

    extensions: list[str] = Field(default_factory=list[str])
    """Поддерживаемы типы"""

    default: bool = Field(default=False)
    """Является ли тип базовым"""


class FileModel(BaseModelMixin):
    """Модель файла"""

    name: str = Field(
        ...,
        description="Наименование",
    )

    description: str = Field(
        ...,
        description="Описание",
    )

    type: FileTypeModel = Field(
        ...,
        description="Тип файла",
    )

    mimetype: str = Field(
        ...,
        description="Тип файла",
    )

    extension: str = Field(
        ...,
        description="Расширение файла",
    )

    size: int = Field(...)
    """Размер"""

    md5_checksum: str = Field(
        ...,
        description="MD5 контрольная сумма",
    )

    sha256_checksum: str = Field(
        ...,
        description="SHA256 контрольная сумма",
    )

    owner: UserModel = Field(...)
    """Владелец файла"""

    is_public: bool = Field(...)
    """Является ли файл публичным"""

    tags: list[FileTagModel] = Field(
        default_factory=list[FileTagModel],
        description="Список тегов",
    )


__all__ = [
    "FileTagModel",
    "FileTypeModel",
    "FileModel",
]
