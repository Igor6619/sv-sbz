from enum import Enum
from uuid import UUID
from typing import Union, Optional
from pydantic import BaseModel, Field, field_validator, field_serializer


class FileSearchType(str, Enum):
    """Тип поиска"""

    Name = "name"
    """Поиск по имени"""

    Keywords = "keywords"
    """Поиск по ключевым словам"""

    Description = "description"
    """Поиск по описанию"""

    Content = "content"
    """Поиск по содержимому"""


class FileSearchTypeName(str, Enum):
    """Тип поиска"""

    Name = "По названию"
    """Поиск по имени"""

    Keywords = "По ключевым словам"
    """Поиск по ключевым словам"""

    Description = "По описанию (векторный)"
    """Поиск по описанию"""

    Content = "Полнотекстовый поиск (векторный)"
    """Поиск по содержимому"""


class AbstractFileSearch(BaseModel):

    name: str = Field(
        ...,
        description="Наименование поиска",
    )

    type: str = Field(
        ...,
        description="Тип поиска",
    )


class FileNameSearch(AbstractFileSearch):
    """Простой поиск файла по имени"""

    type: str = FileSearchType.Name.value
    name: str = FileSearchTypeName.Name.value

    value: str = Field(
        ...,
        description="Наименование",
    )


class FileDescriptionSearch(AbstractFileSearch):
    """Простой поиск файла по описанию"""

    type: str = FileSearchType.Description.value
    name: str = FileSearchTypeName.Description.value

    value: str = Field(
        ...,
        description="Описание",
    )


class FileContentSearch(AbstractFileSearch):
    """Простой поиск файла по описанию"""

    type: str = FileSearchType.Content.value
    name: str = FileSearchTypeName.Content.value

    value: str = Field(
        ...,
        description="Содержимое файла",
    )


class FileKeywordsSearch(AbstractFileSearch):
    """Простой поиск файла по ключевым словам"""

    type: str = FileSearchType.Keywords.value
    name: str = FileSearchTypeName.Keywords.value

    value: list[str] = Field(
        ...,
        description="Список ключевых слов",
    )


FileSearch = Union[
    FileNameSearch, FileDescriptionSearch, FileContentSearch, FileKeywordsSearch
]


class TagModelForGraph(BaseModel):
    id: str = Field(
        ...,
        description="Идентификатор",
    )
    name: str = Field(
        ...,
        description="Наименование",
    )
    type: str = Field(
        default="tag",
        description="Тип ветки"
    )
    children: list["FileModelForGraph"] = Field(
        default_factory=list["FileModelForGraph"],
        description="Список файлов, связанных с тегом"
    )


class FileModelForGraph(BaseModel):
    id: str = Field(
        ...,
        description="Идентификатор",
    )
    name: str = Field(
        ...,
        description="Наименование",
    )
    type: str = Field(
        default="file",
        description="Тип ветки"
    )


class UserUuidResponse(BaseModel):
    """Схема успешного ответа, возвращающая UUID пользователя."""

    uuid: UUID = Field(
        description="Внутренний уникальный идентификатор (UUID) пользователя в системе",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )


class SearchQueryModel(BaseModel):
    value: str = Field(
        default="",
        description="Строка запроса"
    )
    results_count: int = Field(
        default=0,
        description="Количество найденных материалов по запросу",
    )
    count: int = Field(
        default=0,
        description="Количество подобных запросов",
    )


class SearchQueryFilterSchema(BaseModel):
    input_value: Optional[str] = Field(
        default=None,
        description="Полученный поисковый запрос"
    )
    last_days_count: Optional[int] = Field(
        default=30,
        description="Количество последних дней, за которые нужны поисковые запросы",
    )
    results_count: Optional[int] = Field(
        default=None,
        description="Количество материалов, найденных по запросу"
    )
    limit: Optional[int] = Field(
        default=1000,
        description="Ограничение по количеству"
    )
    # TODO offset, limit


__all__ = [
    "FileSearch",
    "AbstractFileSearch",
    "FileNameSearch",
    "FileDescriptionSearch",
    "FileContentSearch",
    "FileKeywordsSearch",
    "FileSearchType",
    "FileSearchTypeName",
    "TagModelForGraph",
    "FileModelForGraph",
    "SearchQueryModel",
    "SearchQueryFilterSchema",
]
