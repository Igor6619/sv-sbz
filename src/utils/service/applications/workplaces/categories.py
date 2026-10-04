from asyncio import to_thread
from requests import Response
from pydantic import TypeAdapter
from .service import CategoriesRepository
from .exceptions import WorkplacesBadRequestsEroor
from ...setting import AuthClientSetting
from ...authentication import AuthRequests
from ...datastructures.workplaces import *


class BaseCategoriesRepository(CategoriesRepository):
    def __init__(
        self,
        requests: AuthRequests,
        setting: AuthClientSetting,
    ):
        super().__init__()
        self.r = requests
        self.s = setting

    async def get(
        self,
        id: str,
    ) -> CategoryModel | None:
        r: Response = await to_thread(
            self.r.get,
            f"{self.s.url}/workplaces/categories",
            params={"id": id},
        )
        if r.status_code == 200:
            try:
                return CategoryModel.model_validate(r.json())
            except Exception as ex:
                print("Get workplace category error", ex)
                return None

        raise WorkplacesBadRequestsEroor(r.url, r)

    async def values(
        self,
        filter: CategoriesFilter | None = None,
    ) -> list[CategoryModel]:
        r: Response = await to_thread(
            self.r.get,
            f"{self.s.url}/workplaces/categories/list",
            params=filter.model_dump() if filter is not None else {},
        )
        if r.status_code == 200:
            try:
                return TypeAdapter(list[CategoryModel]).validate_python(r.json())
            except Exception as ex:
                print("Get workplace categories error", ex)
                return []

        raise WorkplacesBadRequestsEroor(r.url, r)
