from asyncio import to_thread
from requests import Response
from pydantic import TypeAdapter
from .service import WorkplacesRepository
from .exceptions import WorkplacesBadRequestsEroor
from ...setting import AuthClientSetting
from ...datastructures.workplaces import *
from ...authentication import AuthRequests


class BaseWorkplacesRepository(WorkplacesRepository):
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
    ) -> WorkplaceModel | None:
        r: Response = await to_thread(
            self.r.get,
            f"{self.s.url}/workplaces/",
            params={"id": id},
        )
        if r.status_code == 200:
            try:
                return WorkplaceModel.model_validate(r.json())
            except Exception as ex:
                print("Get workplace error", ex)
                return None

        raise WorkplacesBadRequestsEroor(r.url, request=r)

    async def values(
        self,
        filter: WorkplaceFilter | None = None,
    ) -> list[WorkplaceModel]:
        r: Response = await to_thread(
            self.r.get,
            f"{self.s.url}/workplaces/list",
            params=filter.model_dump() if filter is not None else {},
        )
        if r.status_code == 200:
            try:
                return TypeAdapter(list[WorkplaceModel]).validate_python(r.json())
            except Exception as ex:
                print("Get workplaces error", ex)
                return []

        raise WorkplacesBadRequestsEroor(r.url, request=r)
