from asyncio import to_thread
from requests import Response
from pydantic import TypeAdapter
from .service import WorkplacesBusyService

from .exceptions import WorkplacesBadRequestsEroor
from ...setting import AuthClientSetting
from ...authentication import AuthRequests
from ...datastructures.workplaces import *


class BaseWorkplacesBusyService(WorkplacesBusyService):
    def __init__(
        self,
        requests: AuthRequests,
        setting: AuthClientSetting,
    ):
        super().__init__()
        self.r = requests
        self.s = setting

    async def workplaces_by_user(
        self,
        user: str,
    ) -> list[WorkplaceBusyModel]:
        r: Response = await to_thread(
            self.r.get,
            f"{self.s.url}/workplaces/busy/user",
            params={"id": user},
        )
        if r.status_code == 200:
            try:
                return TypeAdapter(list[WorkplaceBusyModel]).validate_python(r.json())
            except Exception as ex:
                print("Get busy workplaces by user error", ex)
                return []

        raise WorkplacesBadRequestsEroor(r.url, request=r)

    async def workplaces(
        self,
        filter: WorkplaceBusyFilter | None = None,
    ) -> list[WorkplaceBusyModel]:
        r: Response = await to_thread(
            self.r.get,
            f"{self.s.url}/workplaces/busy/list",
            params=filter.model_dump() if filter is not None else {},
        )
        if r.status_code == 200:
            try:
                return TypeAdapter(list[WorkplaceBusyModel]).validate_python(r.json())
            except Exception as ex:
                print("Get busy workplaces error", ex)
                return []

        raise WorkplacesBadRequestsEroor(r.url, request=r)
    