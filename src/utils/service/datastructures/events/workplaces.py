from pydantic import BaseModel, Field
from ..auth import User

EVENT_WORKPLACE_OPEN_SESSION = "auth.workplace.open"
"""Код события обновления занятости рабочего места"""

EVENT_WORKPLACE_CLOSE_SESSION = "auth.workplace.close"
"""Код события обновления занятости рабочего места"""

EVENTS_WORLPLACES_SESSIONS = [
    EVENT_WORKPLACE_OPEN_SESSION,
    EVENT_WORKPLACE_CLOSE_SESSION,
]
"""События занятости рабочих мест"""


class WorkplaceEventSchema(BaseModel):
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
        description="Адрес хоста",
    )

    data: dict = Field(
        default_factory=dict,
        description="Дополнительные данные",
    )

    user: User | None = Field(
        default=None,
        description="Пользователь",
    )


__all__ = [
    "EVENT_WORKPLACE_OPEN_SESSION",
    "EVENT_WORKPLACE_CLOSE_SESSION",
    "EVENTS_WORLPLACES_SESSIONS",
    "WorkplaceEventSchema",
]
