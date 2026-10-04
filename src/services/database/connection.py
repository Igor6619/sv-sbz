from settings import SETTING_DB
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(
    url=SETTING_DB.database,
    echo=SETTING_DB.debug_sql,
)
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


@asynccontextmanager
async def database_lifespan(app):
    yield
    engine.dispose()


def create_async_session():
    return async_sessionmaker(
        create_async_engine(
            url=SETTING_DB.database,
            echo=SETTING_DB.debug_sql,
        ),
        expire_on_commit=False,
    )


__all__ = [
    "async_session",
    "database_lifespan",
    "create_async_session",
]
