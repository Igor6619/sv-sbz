from pydantic import BaseModel, Field


class EventSetting(BaseModel):
    """Настройки универсальных событий"""

    url: str = Field(
        default="${EVENTS_SERVICE_URL}",
        description="URL направления события",
    )

    retries: int = Field(
        default=3,
        description="Количество попуток на отправку",
    )
    error_delay_sec: int = Field(
        default=3,
        description="Время ожидания в случае ошибки",
    )


__all__ = ["EventSetting"]
