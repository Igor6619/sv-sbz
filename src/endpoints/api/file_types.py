import os
import json
import uuid

import fastapi
import tempfile
import aiofiles
import pydantic
from depends import *
from services import FileTypeRepository
from utils.sbz.datastuctures.models import FileTypeModel
from utils.sbz.datastuctures.schemas import FileTypeSchema

api_file_types_router = fastapi.routing.APIRouter()


@api_file_types_router.get("/{id}")
async def get_file_type(
    id: str,
    repository: FileTypeRepository = fastapi.Depends(FileTypeRepositoryRequired),
) -> FileTypeModel | None:
    """Получить тип файла по идентификатору"""
    r = await repository.get(uuid.UUID(id))
    return await repository.model_from_orm(r) if r is not None else None


@api_file_types_router.delete("/{id}")
async def delete_file_type(
    id: str,
    repository: FileTypeRepository = fastapi.Depends(AdminFileTypeRepositoryRequired),
):
    """Удалить тип файл по идентификатору"""
    await repository.delete(uuid.UUID(id))


@api_file_types_router.put("")
async def create_file_type(
    schema: FileTypeSchema = fastapi.Body(),
    repository: FileTypeRepository = fastapi.Depends(AdminFileTypeRepositoryRequired),
) -> FileTypeModel:
    """Создать тип файла"""
    return await repository.model_from_orm(await repository.create(schema=schema))


@api_file_types_router.patch("")
async def update_file_model(
    schema: FileTypeSchema = fastapi.Body(),
    repository: FileTypeRepository = fastapi.Depends(AdminFileTypeRepositoryRequired),
) -> FileTypeModel:
    """Обновить тип файла"""
    return await repository.model_from_orm(await repository.update(schema=schema))


@api_file_types_router.get("")
async def get_file_models(
    repository: FileTypeRepository = fastapi.Depends(FileTypeRepositoryRequired),
) -> list[FileTypeModel]:
    """Получить список типов файлов"""
    return await repository.models_from_orm(await repository.values())


@api_file_types_router.post("/import")
async def import_file_types(
    file: fastapi.UploadFile = fastapi.File(),
    repository: FileTypeRepository = fastapi.Depends(AdminFileTypeRepositoryRequired),
) -> list[FileTypeModel]:
    data = json.loads(await file.read())
    schemas = pydantic.TypeAdapter(list[FileTypeSchema]).validate_python(data)

    for item in schemas:
        current = await repository.get(item.id) if item.id is not None else None
        if current is not None:
            await repository.update(item)
        else:
            await repository.create(item)

    return await repository.models_from_orm(await repository.values())


@api_file_types_router.post("/export")
async def export_file_types(
    repository: FileTypeRepository = fastapi.Depends(FileTypeRepositoryRequired),
) -> fastapi.responses.StreamingResponse:
    models = await repository.models_from_orm(await repository.values())
    data = pydantic.TypeAdapter(list[FileTypeModel]).dump_json(models)

    async def gen():
        yield data

    return fastapi.responses.StreamingResponse(
        gen(), media_type="application/json", status_code=200
    )


__all__ = [
    "api_file_types_router",
]
