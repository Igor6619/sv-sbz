from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator


class CategoriesFilter(BaseModel):
    id: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список пользователей",
    )

    @field_validator("id", mode="before")
    def validate_str_list(cls, v: str):
        if v is not None and isinstance(v, list):
            v = ",".join(v)

        if v is not None and isinstance(v, str):
            return list(filter(lambda x: len(x) > 0, [i.strip() for i in v.split(",")]))

        return v


class WorkplaceFilter(BaseModel):
    id: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список пользователей",
    )

    @field_validator("id", mode="before")
    def validate_str_list(cls, v: str):
        if v is not None and isinstance(v, list):
            v = ",".join(v)

        if v is not None and isinstance(v, str):
            return list(filter(lambda x: len(x) > 0, [i.strip() for i in v.split(",")]))

        return v


class WorkplaceBusyFilter(BaseModel):

    workplace: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список рабочих мест",
    )

    category: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Список категорий рабочих мест",
    )

    @field_validator("workplace", "category", mode="before")
    def validate_str_list(cls, v: str):
        if v is not None and isinstance(v, list):
            v = ",".join(v)

        if v is not None and isinstance(v, str):
            return list(filter(lambda x: len(x) > 0, [i.strip() for i in v.split(",")]))

        return v
