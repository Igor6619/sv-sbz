from typing import Optional, Union
from pydantic import BaseModel, Field


class EventRequestSchema(BaseModel):
    """Схема отправкисобытия"""

    id: str = Field(
        ...,
        description="Код события",
    )

    receivers: Optional[list[str]] = Field(
        default=None,
        description="Список получателей",
    )

    data: Optional[
        Union[
            str,
            float,
            int,
            list,
            dict,
        ]
    ] = Field(
        default=None,
        description="Данные события",
    )


class EventSchema(EventRequestSchema):
    """Схема входящего события"""

    sender: Optional[str] = Field(
        default=None,
        description="Отправитель сообщения",
    )


__all__ = [
    "EventSchema",
    "EventRequestSchema",
]
