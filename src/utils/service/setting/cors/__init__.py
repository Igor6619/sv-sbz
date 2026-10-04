from pydantic import BaseModel, Field


class CorsSetting(BaseModel):
    """Настройки CORS"""

    allow_origins: list[str] = Field(default=["http://127.0.0.1", "https://127.0.0.1"])
    """Список разрешённых источников"""

    allow_credentials: bool = Field(default=True)
    """Разрешить учётные данные (куки, Authorization)"""

    allow_methods: list[str] = Field(default=["*"])
    """Разрешенные методы"""

    allow_headers: list[str] = Field(default=["*"])
    """Разрешенные заголовки"""


__all__ = ["CorsSetting"]
