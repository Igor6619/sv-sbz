from uuid import UUID
from pydantic import TypeAdapter
from abc import ABC, abstractmethod
from starlette.exceptions import HTTPException
from ...settings import SbzSetting
from ...datastuctures.models import *
from ...datastuctures.schemas import *
from ....service import AuthRequests


class SbzFileTypeRepository(ABC):
    """Репозиторий типов файлов специализированной базы знаний"""

    @abstractmethod
    def get(self, id: UUID) -> FileTypeModel | None:
        """Получить информацию о типе файла"""

    @abstractmethod
    def values(self) -> list[FileTypeModel]:
        """Получить список типов файлов"""


class _SbzFileTypeRepository(SbzFileTypeRepository):
    def __init__(
        self,
        requests: AuthRequests,
        setting: SbzSetting,
    ):
        super().__init__()
        self._r = requests
        self._s = setting

    def get(self, id: UUID) -> FileModel | None:
        r = self._r.get(f"{self._s.url}/api/types/{str(id)}")
        if r.status_code == 200:
            return FileTypeModel.model_validate(r.json())
        return None
        
            

    def values(self) -> list[FileTypeModel]:
        r = self._r.get(
            f"{self._s.url}/api/types",
        )
        if r.status_code == 200:
            return TypeAdapter(list[FileTypeModel]).validate_python(r.json())

        raise HTTPException(status_code=r.status_code, detail=r.content)

def create_sbz_file_type_repository(
    requests: AuthRequests,
    setting: SbzSetting,
) -> SbzFileTypeRepository:
    return _SbzFileTypeRepository(
        requests=requests,
        setting=setting,
    )


__all__ = [
    "SbzFileTypeRepository",
    "create_sbz_file_type_repository",
]
