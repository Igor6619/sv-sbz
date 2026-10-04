import os
from pydantic import BaseModel, Field


class DataBaseSetting(BaseModel):
    debug_sql: bool = Field(
        default=os.environ.get("DATABASE_DEBUG", "False").lower().strip()
        in ["true", "yes", "on", "1"],
        description="Выводить SQL запросы",
    )

    database: str = Field(
        default="${DATABASE_URL}",
        description="Строка подключения к БД",
    )


__all__ = ["DataBaseSetting"]
