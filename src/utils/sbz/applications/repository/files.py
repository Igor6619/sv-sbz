import os
from uuid import UUID
from pydantic import TypeAdapter
from abc import ABC, abstractmethod
from starlette.datastructures import FormData, UploadFile
from starlette.exceptions import HTTPException
from ...settings import SbzSetting
from ...datastuctures.models import *
from ...datastuctures.schemas import *
from ....service import AuthRequests


class SbzFilesRepository(ABC):
    """Репозиторий файлов специализированной базы знаний"""

    @abstractmethod
    def get(self, id: UUID) -> FileModel | None:
        """Получить информацию о файле"""

    @abstractmethod
    def values(self, filter: FileFilterSchema) -> list[FileModel]:
        """Получить список файлов ао фильтру"""

    @abstractmethod
    def url(self, id: UUID) -> str:
        """Получить ссылку на файл"""
        
    @abstractmethod
    def preview_url(self, id: UUID) -> str:
        """URL просмтора файла"""


class SbzFilesRepositoryImpl(SbzFilesRepository):
    def __init__(
        self,
        requests: AuthRequests,
        setting: SbzSetting,
    ):
        super().__init__()
        self._r = requests
        self._s = setting

    def get(self, id: UUID) -> FileModel | None:
        r = self._r.get(f"{self._s.url}/api/files/{str(id)}")
        if r.status_code == 200:
            return FileModel.model_validate(r.json())
        return None

    def upload(self, schema: FileSchema, file: str) -> FileModel:
        with open(os.path.abspath(file), "rb") as f:
            form = FormData(
                {
                    **self._file_schema_to_form_data(schema),
                    "file": UploadFile(
                        f,
                        filename=os.path.basename(file),
                    ),
                }
            )
            r = self._r.put(
                f"{self._s.url}/api/files",
                data=form,
                check_responce=lambda r: r.status_code == 200,
            )

            return FileModel.model_validate(r.json())
        
    def update(self, schema: FileSchema, file: str | None = None) -> FileModel: 
        if file is not None: 
            with open(os.path.abspath(file), "rb") as f:
                form = FormData(
                    {
                        **self._file_schema_to_form_data(schema),
                        "file": UploadFile(
                            f,
                            filename=os.path.basename(file),
                        ),
                    }
                )
                r = self._r.patch(
                    f"{self._s.url}/api/files",
                    data=form,
                    check_responce=lambda r: r.status_code == 200,
                )

                return FileModel.model_validate(r.json())
        else: 
            form = FormData(
                {
                    **self._file_schema_to_form_data(schema),
                    "file": UploadFile(
                        f,
                        filename=os.path.basename(file),
                    ),
                }
            )
            r = self._r.patch(
                f"{self._s.url}/api/files",
                data=form,
                check_responce=lambda r: r.status_code == 200,
            )

            return FileModel.model_validate(r.json())
            
            

    def values(self, filter: FileFilterSchema) -> list[FileModel]:
        r = self._r.post(
            f"{self._s.url}/api/files",
            json=filter.model_dump(),
        )
        if r.status_code == 200:
            return TypeAdapter(list[FileModel]).validate_python(r.json())

        raise HTTPException(status_code=r.status_code, detail=r.content)

    def url(self, id: UUID) -> str:
        return f"{self._s.url}/api/files/{str(id)}/download?{'&'.join([ f'{str(k)}={str(v)}' for k, v in self._r.url_credentials().items()])}"

    def preview_url(self, id: UUID) -> str:
        return f"{self._s.url}/api/files/{str(id)}/preview?{'&'.join([ f'{str(k)}={str(v)}' for k, v in self._r.url_credentials().items()])}"
    
    def _file_schema_to_form_data(self, schema: FileSchema) -> dict[str, str]:
        data = schema.model_dump(exclude_none=True)
        for k in data.keys(): 
            v = data[k]
            if isinstance(v, list): 
                data[k] = [str(i) for i in v]
            elif isinstance(v, UUID): 
                data[k] = v
        return data

def create_sbz_files_repository(
    requests: AuthRequests,
    setting: SbzSetting,
) -> SbzFilesRepository:
    return SbzFilesRepositoryImpl(
        requests=requests,
        setting=setting,
    )


__all__ = [
    "SbzFilesRepository",
    "create_sbz_files_repository",
]
