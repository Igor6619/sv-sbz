from sqlalchemy.ext.asyncio import AsyncSession
from services.database import async_session


async def DatabaseSessionRequired() -> AsyncSession:
    async with async_session() as session:
        yield session


__all__ = ["DatabaseSessionRequired"]
