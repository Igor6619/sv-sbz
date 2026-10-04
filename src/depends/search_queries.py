import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from depends import DatabaseSessionRequired
from services.search_query import SearchQueryRepository, create_search_query_repository
from utils.service import AuthUserEnvrimoment, AuthEnvrimomentOrNone


async def SearchQueryRepositoryRequired(
    env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
    db: AsyncSession = fastapi.Depends(DatabaseSessionRequired),
) -> SearchQueryRepository:
    return create_search_query_repository(env=env, database=db)


__all__ = ["SearchQueryRepositoryRequired"]
