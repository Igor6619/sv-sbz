from pydantic import BaseModel, Field, field_validator


class RedisSetting(BaseModel):
    """Настройки Redis"""

    host: str = Field(
        default="${REDIS_HOST}",
        description="Хост Redis",
    )
    port: int = Field(
        default="${REDIS_PORT}",
        description="Порт Redis",
    )
    db: int = Field(
        default="${REDIS_DATABASE}",
        description="База данных Redis",
    )

    @field_validator("port", "db", mode="before")
    @classmethod
    def str_int_validator(cls, v) -> int:
        if isinstance(v, str):
            return int(v)
        return v


__all__ = ["RedisSetting"]
