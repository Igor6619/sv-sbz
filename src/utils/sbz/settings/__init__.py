from pydantic import BaseModel, Field


class SbzSetting(BaseModel):
    """Настройки клиента специализированной базы знаний"""

    url: str = Field(
        default="${SBZ_SERVICE_URL}",
        description="URL сервиса СБЗ",
    )


__all__ = ["SbzSetting"]
