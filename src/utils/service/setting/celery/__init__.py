from pydantic import BaseModel, Field


class CelerySetting(BaseModel):

    broker: str = Field(
        default="${CELERY_BROKER}",
        description="Путь до брокера сообщений",
    )

    backend: str = Field(
        default="${CELERY_BACKEND}",
        description="Путь до брокера сообщений результатов",
    )


__all__ = ["CelerySetting"]
