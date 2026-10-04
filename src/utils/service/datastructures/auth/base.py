from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ...tools import PydanticHelper
from .user import User


class Token(BaseModel, PydanticHelper.mixins.datetime("access_expires")):
    """Представление хранения информации о токене"""

    user: str = Field(
        default="",
        description="Идентификатор пользователя",
    )

    access: str = Field(
        default="",
        description="Идентификатор доступа",
    )

    access_expires: Optional[datetime] = Field(
        default=None,
        description="Время жизни токена",
    )


class AuthData(BaseModel):
    jwt: str
    user: User
    token: Token
