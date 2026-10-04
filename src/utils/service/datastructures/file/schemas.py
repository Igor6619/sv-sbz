from uuid import UUID
from typing import Optional, Literal
from pydantic import BaseModel, Field
from ...tools import PydanticHelper


class FileTypeSchema(BaseModel, PydanticHelper.mixins.uuid("id")):
    """Схема типа файла"""

    id: Optional[UUID] = Field(default=None)
    """Идентификатор"""

    name: Optional[str] = Field(default=None)
    """Наименование"""

    code: Optional[str] = Field(default=None)
    """Код типа файла"""


class FileSchema(
    BaseModel,
    PydanticHelper.mixins.uuid("id", "type"),
    PydanticHelper.mixins.uuid_list("tags"),
    PydanticHelper.mixins.str_list("keywords"),
):
    """Схема файла"""

    id: Optional[UUID] = Field(default=None)
    """Идентификатор"""

    type: Optional[UUID] = Field(default=None)
    """Идентифкатор типа файла"""
    
    type_code: Optional[str] = Field(default=None)
    """Код типа файла"""

    name: Optional[str] = Field(default=None)
    """Наименование"""

    description: Optional[str] = Field(default=None)
    """Описание"""

    mimetype: Optional[str] = Field(default=None)
    """Тип файла"""

    tags: Optional[list[UUID]] = Field(default=None)
    """Список тегов"""

    keywords: Optional[list[str]] = Field(default=None)
    """Список ключевых слов"""

    mimetype: Optional[bool] = Field(default=False)
    """Является ли общелоступным"""


class FileFilterSchema(
    BaseModel,
    PydanticHelper.mixins.str_list("names", "descriptions", "type_codes", "mimetypes", "extensions"),
    PydanticHelper.mixins.uuid_list("ids", "types"),
):
    """Фильт для поиска файлов и директорий"""

    ids: Optional[list[UUID]] = Field(default=None)
    """Список идентиифкаторов файлов"""
    
    names: Optional[list[str]] = Field(default=None)
    """Название или список названий элементов"""

    descriptions: Optional[list[str]] = Field(default=None)
    """Список описания вхождения"""

    types: Optional[list[UUID]] = Field(default=None)
    """Список типов файлов"""

    type_codes: Optional[list[str]] = Field(default=None)
    """Коды типов"""
    
    mimetypes: Optional[list[str]] = Field(default=None)
    """Mimetype или список mimetype"""

    extensions: Optional[list[str]] = Field(default=None)
    """Расширение файла или список расширений файлов"""

    owner_type: Optional[Literal["my", "common", "all"]] = Field(default=None)
    """Тип владельца"""

    offset: Optional[int] = Field(default=None)
    """Сдвиг диапазона"""

    limit: Optional[int] = Field(default=None)
    """Максимальное количество записей"""


__all__ = ["FileTypeSchema", "FileSchema", "FileFilterSchema"]
