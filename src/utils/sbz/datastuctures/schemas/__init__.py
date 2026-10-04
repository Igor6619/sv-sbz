from uuid import UUID
from datetime import datetime
from typing import Optional, Union, Literal
from pydantic import BaseModel, Field
from ....service.tools import PydanticHelper


class FileTypeSchema(BaseModel, PydanticHelper.mixins.uuid("id")):
    id: Optional[UUID] = Field(
        default=None,
        description="Идентификатор",
    )

    name: Optional[str] = Field(
        default=None,
        description="Наименование",
    )

    code: Optional[str] = Field(
        default=None,
        description="Код типа файла",
    )

    extensions: Optional[list[str]] = Field(default=None)
    """Поддерживаемы типы"""

    default: bool = Field(default=False)
    """Является ли тип базовым"""


class FileTagSchema(BaseModel, PydanticHelper.mixins.uuid("id", "parent")):
    """Схема тега"""

    id: Optional[UUID] = Field(
        default=None,
        description="Идентификатор",
    )

    code: Optional[str] = Field(
        default=None,
        description="Код",
    )

    name: Optional[str] = Field(
        default=None,
        description="Наименование",
    )

    parent: Optional[UUID] = Field(
        default=None,
        description="Идентификатор родительского тега",
    )

    keyword: Optional[bool] = Field(
        default=False,
        description="Принадлежность к ключевым словам",
    )

    children: Optional[list["FileTagSchema"]] = Field(
        default=None,
        description="Список дочерних тегов",
    )


class FileTagFilterSchema(
    BaseModel,
    PydanticHelper.mixins.uuid_list("id", "parent"),
    PydanticHelper.mixins.str_list("code", "exclude_code", "name"),
):
    """Фильтр поиска файлов"""

    id: Optional[Union[UUID, list[UUID]]] = Field(
        default=None,
        description="Список идентификаторов файлов",
    )

    code: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список кодов вхождения разделенных запятой",
    )

    exclude_code: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список кодов исключения разделенных запятой",
    )

    name: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список имен вхождения разделенных запятой",
    )

    parent: Optional[Union[UUID, list[UUID]]] = Field(
        default=None,
        description="Список идентификаторов родительских тегов",
    )

    keyword: Optional[bool] = Field(
        default=None,
        description="Принадлежность к ключевым словам",
    )


class FileSchema(
    BaseModel,
    PydanticHelper.mixins.uuid("id", "type"),
    PydanticHelper.mixins.uuid_list("tags"),
    PydanticHelper.mixins.str_list("keywords"),
):
    """Схема файла"""

    id: Optional[UUID] = Field(
        default=None,
        description="Идентификатор",
    )

    type: Optional[UUID] = Field(
        default=None,
        description="Интедифкатор типа файла",
    )

    type_code: Optional[str] = Field(
        default=None,
        description="Код типа файла",
    )

    name: Optional[str] = Field(
        default=None,
        description="Наименование",
    )

    description: Optional[str] = Field(
        default=None,
        description="Описание",
    )

    mimetype: Optional[str] = Field(
        default=None,
        description="Тип файла",
    )

    tags: Optional[list[UUID]] = Field(
        default=None,
        description="Список тегов",
    )

    keywords: Optional[list[str]] = Field(
        default=None,
        description="Список ключевых слов",
    )

    is_public: Optional[bool] = Field(
        default=True,
        description="Публичный файл",
    )


class FileFilterSchema(
    BaseModel,
    PydanticHelper.mixins.uuid_list("id", "type", "tag"),
    PydanticHelper.mixins.str_list(
        "name", "description", "type_code", "extension", "mimetype", "keyword", "owner"
    ),
    PydanticHelper.mixins.datetime(
        "created_begin", "created_end", "updated_begin", "updated_end"
    ),
):
    """Фильтр поиска файлов"""

    id: Optional[Union[UUID, list[UUID]]] = Field(
        default=None,
        description="Список идентификаторов файлов",
    )

    name: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список имен вхождения разделенных запятой",
    )

    description: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список описания вхождения разделенных запятой",
    )

    type: Optional[Union[UUID, list[UUID]]] = Field(
        default=None,
        description="Список типов файлов",
    )

    type_code: Optional[Union[str, list[str]]] = Field(
        default=None, description="Коды типов"
    )

    extension: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список расширений файлов",
    )

    mimetype: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список mimetype",
    )

    keyword: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список ключевых слов",
    )

    tag: Optional[Union[UUID, list[UUID]]] = Field(
        default=None,
        description="Список идентификаторов тегов",
    )

    created_begin: Optional[datetime] = Field(
        default=None,
        description="Начала диапозона времени создания",
    )

    created_end: Optional[datetime] = Field(
        default=None,
        description="Конец диапозона времени создания",
    )

    updated_begin: Optional[datetime] = Field(
        default=None,
        description="Начала диапозона времени обновления",
    )

    updated_end: Optional[datetime] = Field(
        default=None,
        description="Конец диапозона времени обновления",
    )

    owner: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Владелецц файла",
    )

    owner_type: Optional[Literal["my", "common", "all"]] = Field(default=None)
    """Тип владельца"""

    enabled: Optional[bool] = Field(
        default=True,
        description="True - только не удаленные, False - только удаленные, None - все",
    )

    offset: Optional[int] = Field(
        default=None,
        description="Сдвиг диапазона",
    )

    limit: Optional[int] = Field(
        default=None,
        description="Максимальное количество записей",
    )


__all__ = [
    "FileTypeSchema",
    "FileTagSchema",
    "FileSchema",
    "FileFilterSchema",
    "FileTagFilterSchema",
]
