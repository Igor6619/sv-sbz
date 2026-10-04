from uuid import UUID
from pydantic import TypeAdapter
from abc import ABC, abstractmethod
from starlette.exceptions import HTTPException
from ...settings import SbzSetting
from ...datastuctures.models import *
from ...datastuctures.schemas import *
from ....service import AuthRequests


class SbzTagsRepository(ABC):
    """Репозиторий тегов специализированной базы знаний"""

    @abstractmethod
    def get(self, id: UUID) -> FileTagModel | None:
        """Получить информацию о теге"""

    @abstractmethod
    def values(self) -> list[FileTagModel]:
        """Получить список тегов"""


class _SbzTagsRepository(SbzTagsRepository):
    def __init__(
        self,
        requests: AuthRequests,
        setting: SbzSetting,
    ):
        super().__init__()
        self._r = requests
        self._s = setting

    def get(self, id: UUID) -> FileModel | None:
        r = self._r.get(f"{self._s.url}/api/tags/{str(id)}")
        if r.status_code == 200:
            return FileTagModel.model_validate(r.json())
        return None
        
            

    def values(self) -> list[FileTagModel]:
        r = self._r.get(
            f"{self._s.url}/api/tags",
        )
        if r.status_code == 200:
            return TypeAdapter(list[FileTagModel]).validate_python(r.json())

        raise HTTPException(status_code=r.status_code, detail=r.content)

def create_sbz_tags_repository(
    requests: AuthRequests,
    setting: SbzSetting,
) -> SbzTagsRepository:
    return _SbzTagsRepository(
        requests=requests,
        setting=setting,
    )


__all__ = [
    "SbzTagsRepository",
    "create_sbz_tags_repository",
]
