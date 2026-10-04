from datetime import datetime
from pydantic import BaseModel, Field
from ..auth import User
from ...tools import PydanticHelper

EVENT_OPEN_SESSION = "auth.login"
"""Код события входа пользователя"""

EVENT_UPDATE_SESSION = "auth.update"
"""Код события продления сесии пользователя"""

EVENT_CLOSE_SESSION = "auth.close"
"""Код события закрытия сессии пользователя"""

EVENTS_AUTH_SESSIONS = [
    EVENT_OPEN_SESSION,
    EVENT_UPDATE_SESSION,
    EVENT_CLOSE_SESSION,
]
"""События открытия и закрытия сесиий"""


class AuthEventSchema(BaseModel, PydanticHelper.mixins.datetime("expires")):
    id: str = Field(
        ...,
        description="Идентификатор сесии",
    )

    user: User = Field(
        ...,
        description="Пользователь",
    )

    host: str = Field(
        ...,
        description="Адрес хоста с которого осуществлен вход",
    )

    expires: datetime = Field(
        ...,
        description="Время жизни",
    )


__all__ = [
    "EVENT_OPEN_SESSION",
    "EVENT_CLOSE_SESSION",
    "EVENT_UPDATE_SESSION",
    "EVENTS_AUTH_SESSIONS",
    "AuthEventSchema",
]
