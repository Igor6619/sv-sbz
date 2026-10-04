import os
from typing import List

import fastapi
from fastapi.templating import Jinja2Templates
from pydantic import TypeAdapter

from depends import SearchQueryRepositoryRequired
from schemas import SearchQueryModel, SearchQueryFilterSchema
from services.search_query import SearchQueryRepository

api_search_queries_router = fastapi.routing.APIRouter()
templates = Jinja2Templates(
    directory=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    )
)


@api_search_queries_router.get("/get_search_queries")
async def get_search_queries(
    schema: SearchQueryFilterSchema = fastapi.Query(),
    repository: SearchQueryRepository = fastapi.Depends(SearchQueryRepositoryRequired)
) -> list:
    search_queries = await repository.models_from_orm(await repository.values(schema=schema))
    best_suggestions = {}
    for query in search_queries:
        if query.value not in best_suggestions or query.results_count > best_suggestions[query.value].results_count:
            best_suggestions[query.value] = query
        best_suggestions[query.value].count += 1
    return [query.model_dump() for query in best_suggestions.values()]

__all__ = ["api_search_queries_router"]
