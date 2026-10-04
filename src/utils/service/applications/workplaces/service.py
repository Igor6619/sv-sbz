from abc import ABC, abstractmethod
from ...datastructures.workplaces import (
    CategoryModel,
    CategoriesFilter,
    WorkplaceModel,
    WorkplaceFilter,
    WorkplaceBusyModel,
    WorkplaceBusyFilter,
)


class CategoriesRepository(ABC):
    """Репозиторий категорий рабочих мест"""

    @abstractmethod
    async def get(
        self,
        id: str,
    ) -> CategoryModel | None:
        """Возвращает выбранную категорию"""
        ...

    @abstractmethod
    async def values(
        self,
        filter: CategoriesFilter | None = None,
    ) -> list[CategoryModel]:
        """Возвращает список категорий с связанными рабочими местами"""
        ...


class WorkplacesRepository(ABC):
    """Сервис работы с рабочими местами"""

    @abstractmethod
    async def get(
        self,
        id: str,
    ) -> WorkplaceModel | None:
        """Возвращает рабочее место"""
        ...

    @abstractmethod
    async def values(
        self,
        filter: WorkplaceFilter | None = None,
    ) -> list[WorkplaceModel]:
        """Возвращает список рабочих мест"""
        ...


class WorkplacesBusyService(ABC):
    """Сервис работы с занятостью рабочих мест"""

    @abstractmethod
    async def workplaces_by_user(
        self,
        user: str,
    ) -> list[WorkplaceBusyModel]:
        """Получение списка рабочих мест занятых пользователем"""
        ...

    @abstractmethod
    async def workplaces(
        self,
        filter: WorkplaceBusyFilter | None = None,
    ) -> list[WorkplaceBusyModel]:
        """Возвращает список рабочих мест с указанием пользователя"""
        ...


class WorkplaceService(ABC):
    """Сервис работы с рабочими сестами"""

    @property
    @abstractmethod
    def categories(self) -> CategoriesRepository:
        """Репозиторий категорий рабочих мест"""
        ...

    @property
    @abstractmethod
    def workplaces(self) -> WorkplacesRepository:
        """Реаозиторий рабочих мест"""
        ...

    @property
    @abstractmethod
    def busy(self) -> WorkplacesBusyService:
        """Сервис просмотра занятости рабочих мест"""
        ...
