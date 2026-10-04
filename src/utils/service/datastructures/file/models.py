from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from ..auth.user import UserModel
from ...tools import PydanticHelper


class FileTagModel(BaseModel, PydanticHelper.mixins.uuid("id")):
    """Модель тега"""

    id: UUID = Field(...)
    """Идентификатор"""

    name: str = Field(...)
    """Наименование"""

    code: Optional[str] = Field(default=None)
    """Код"""

    keyword: bool = Field(...)
    """Является ли ключевым словом"""

    children: list["FileTagModel"] = Field(default_factory=list["FileTagModel"])
    """Список дочерних тегов"""


class FileTypeModel(BaseModel, PydanticHelper.mixins.uuid("id")):
    """Представление типа файла"""

    id: UUID = Field(...)
    """Идентификатор"""

    name: str = Field(...)
    """Наименование"""

    code: Optional[str] = Field(default=None)
    """Код"""


class FileModel(BaseModel, PydanticHelper.mixins.uuid("id"), PydanticHelper.mixins.datetime("created", "modified")):
    """Модель файла"""

    id: Optional[UUID] = Field(default=None)
    """Идентификатор"""

    type: Optional[FileTypeModel] = Field(default=None)
    """Тип файла"""

    name: Optional[str] = Field(default=None)
    """Наименование"""

    description: Optional[str] = Field(default=None)
    """Описание"""

    mimetype: Optional[str] = Field(default=None)
    """Тип файла"""

    extension: Optional[str] = Field(default=None)
    """Расширение файла"""

    owner: Optional[UserModel] = Field(default=None)
    """Владелец"""
    
    is_public: Optional[bool] = Field(default=None)
    """Является ли файл публичным"""

    size: Optional[int] = Field(default=None)
    """Размер"""

    md5_checksum: Optional[str] = Field(default=None)
    """MD5 контрольная сумма"""

    sha256_checksum: Optional[str] = Field(default=None)
    """SHA256 контрольная сумма"""

    tags: list[FileTagModel] = Field(default_factory=list[FileTagModel])
    """Список тегов"""

    created: datetime = Field(...)
    """Время создания"""

    modified: datetime = Field(...)
    """Время последнего изменения"""


__all__ = ["FileModel", "FileTagModel", "FileTypeModel"]
