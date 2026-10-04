from pydantic import BaseModel, Field
from ..auth import User


class WorkplaceModel(BaseModel):
    """Модель рабочего места"""

    id: str = Field(
        ...,
        description="Строковый индификатор",
    )

    name: str = Field(
        ...,
        description="Наименование",
    )

    host: str = Field(
        ...,
        description='Адрес хоста',
    )

    data: dict = Field(
        default_factory=dict,
        description="Дополнительные данные",
    )


class CategoryModel(BaseModel):
    """Модель категрий рабочего места"""

    id: str = Field(
        ...,
        description="Строковый индификатор",
    )

    name: str = Field(
        ...,
        description="Наименование",
    )

    data: dict = Field(
        default_factory=dict,
        description="Дополнительные данные",
    )

    workplaces: list[WorkplaceModel] = Field(
        default_factory=list,
        description="Список рабочих мест",
    )


class WorkplaceBusyModel(BaseModel):
    """Модель занятости рабочего места"""

    id: str = Field(
        ...,
        description="Строковый индификатор",
    )

    name: str = Field(
        ...,
        description="Наименование рабочего места",
    )

    data: dict = Field(
        default_factory=dict,
        description="Дополнительные данные",
    )

    users: list[User] = Field(
        default_factory=list,
        description="Пользователь",
    )