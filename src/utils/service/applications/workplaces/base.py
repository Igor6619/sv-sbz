from ...authentication import AuthRequests
from ...setting import AuthClientSetting
from .service import (
    WorkplaceService,
    CategoriesRepository,
    WorkplacesRepository,
    WorkplacesBusyService,
)
from .categories import BaseCategoriesRepository
from .workplaces import BaseWorkplacesRepository
from .busy import BaseWorkplacesBusyService


class BaseWorkplaceService(WorkplaceService):
    def __init__(
        self,
        requests: AuthRequests,
        setting: AuthClientSetting,
    ):
        super().__init__()
        self.r = requests
        self.s = setting

        self.c = BaseCategoriesRepository(
            requests=requests,
            setting=setting,
        )

        self.w = BaseWorkplacesRepository(
            requests=requests,
            setting=setting,
        )

        self.b = BaseWorkplacesBusyService(
            requests=requests,
            setting=setting,
        )

    @property
    def categories(self) -> CategoriesRepository:
        return self.c

    @property
    def workplaces(self) -> WorkplacesRepository:
        return self.w

    @property
    def busy(self) -> WorkplacesBusyService:
        return self.b