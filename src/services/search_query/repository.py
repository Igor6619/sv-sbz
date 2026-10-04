from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models import SearchQueryOrmModel
from schemas import SearchQueryModel, SearchQueryFilterSchema
from utils.service import AuthUserEnvrimoment


class SearchQueryRepository(ABC):
    """Репозиторий поисковых запросов"""

    @abstractmethod
    async def get(self, id: UUID) -> SearchQueryOrmModel | None:
        """Получение поискового запроса"""

    @abstractmethod
    async def add(self, search_query: SearchQueryModel) -> SearchQueryOrmModel:
        """Добавление поискового запроса"""

    @abstractmethod
    async def get_all(self) -> list[SearchQueryOrmModel]:
        """Получение всех поисковых запросов"""

    @abstractmethod
    async def values(self, schema: SearchQueryFilterSchema) -> list[SearchQueryOrmModel]:
        """Получение поисковых запросов по фильтру"""

    @abstractmethod
    async def update(self, search_query: SearchQueryModel) -> SearchQueryOrmModel:
        """Обновление поискового запроса"""

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удаление поискового запроса"""

    @abstractmethod
    async def model_from_orm(self, orm: SearchQueryOrmModel) -> SearchQueryModel:
        """Преобразование в Pydantic модель"""

    @abstractmethod
    async def models_from_orm(self, orm: list[SearchQueryOrmModel]) -> list[SearchQueryModel]:
        """Преобразование в список Pydantic моделей"""


class SearchQueryRepositoryImpl(SearchQueryRepository):
    def __init__(
        self,
        env: AuthUserEnvrimoment,
        database: AsyncSession,
    ):
        super().__init__()
        self.env = env
        self.db = database

    async def get(self, id: UUID) -> SearchQueryOrmModel | None:
        return await self.db.get(SearchQueryOrmModel, id)

    async def add(self, search_query: SearchQueryModel) -> SearchQueryOrmModel:
        orm = SearchQueryOrmModel(
            value=search_query.value.strip().lower(),
            results_count=search_query.results_count
        )
        self.db.add(orm)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(orm)
        return await self.get(orm.id)

    async def get_all(self) -> list[SearchQueryOrmModel]:
        return list((await self.db.execute(select(SearchQueryOrmModel))).scalars().all())

    async def values(self, schema: SearchQueryFilterSchema) -> list[SearchQueryOrmModel]:
        # TODO offset, limit
        query = select(SearchQueryOrmModel)
        if schema.results_count and schema.results_count > 0:
            query = query.where(SearchQueryOrmModel.results_count > schema.results_count)
        else:
            query = query.where(SearchQueryOrmModel.results_count > 0)
        if schema.last_days_count:
            start_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=schema.last_days_count)
            query = query.where(SearchQueryOrmModel.created >= start_date)
        if schema.input_value:
            input_value = schema.input_value.strip().lower()
            query = query.where(
                or_(
                    SearchQueryOrmModel.value.ilike(f"{input_value}%"),
                    SearchQueryOrmModel.value.ilike(f"%{input_value}%"),
                    SearchQueryOrmModel.value.ilike(f"%{input_value}")
                )
            )
        query = query.order_by(desc(SearchQueryOrmModel.created))
        if schema.limit:
            query = query.limit(schema.limit)
        values: list[SearchQueryOrmModel] = list((await self.db.execute(query)).scalars().all())
        return values

    async def update(self, search_query: SearchQueryModel) -> SearchQueryOrmModel:
        raise NotImplementedError(f"Метод изменения поискового запроса не реализован")

    async def delete(self, id: UUID) -> None:
        orm = await self.db.get(SearchQueryOrmModel, id)
        if orm is not None:
            orm.deleted = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.flush()
            await self.db.commit()

    async def model_from_orm(self, orm: SearchQueryOrmModel) -> SearchQueryModel:
        return SearchQueryModel(
            value=orm.value,
            results_count=orm.results_count
        )

    async def models_from_orm(self, orm: list[SearchQueryOrmModel]) -> list[SearchQueryModel]:
        return [await self.model_from_orm(item) for item in orm]


def create_search_query_repository(
    env: AuthUserEnvrimoment,
    database: AsyncSession,
) -> SearchQueryRepository:
    return SearchQueryRepositoryImpl(env, database)


__all__ = ["SearchQueryRepository", "create_search_query_repository"]
