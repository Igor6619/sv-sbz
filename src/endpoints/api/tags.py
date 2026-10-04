import uuid
import json
import fastapi
import pydantic
from depends import *
from schemas import TagModelForGraph
from services import FileTagRepository
from utils.sbz.datastuctures.models import FileTagModel
from utils.sbz.datastuctures.schemas import FileTagSchema, FileTagFilterSchema

api_file_tags_router = fastapi.routing.APIRouter()


@api_file_tags_router.post("/import")
async def import_file_tags(
    file: fastapi.UploadFile,
    repository: FileTagRepository = fastapi.Depends(AdminFileTagRepositoryRequired),
) -> list[FileTagModel]:
    data = json.loads(await file.read())
    schemas = pydantic.TypeAdapter(list[FileTagSchema]).validate_python(data)

    async def insert(item: FileTagSchema) -> FileTagModel:
        result = await repository.create(item)
        for child in item.children if item.children is not None else []:
            child.parent = result.id
            await insert(child)
        return result

    result = []
    for item in schemas:
        result.append(await insert(item))

    result = await repository.values(FileTagFilterSchema(id=[t.id for t in result]))
    return await repository.models_from_orm(result)


@api_file_tags_router.get("/export")
async def export_file_tags(
    repository: FileTagRepository = fastapi.Depends(FileTagRepositoryRequired),
):
    """Получить список тегов в формате JSON"""
    models = await repository.models_from_orm(await repository.values())
    data = pydantic.TypeAdapter(list[FileTagModel]).dump_json(models)

    async def gen():
        yield data

    return fastapi.responses.StreamingResponse(
        gen(), media_type="application/json", status_code=200
    )


@api_file_tags_router.get("/{id}")
async def get_file_tag(
    id: str,
    repository: FileTagRepository = fastapi.Depends(FileTagRepositoryRequired),
) -> FileTagModel | None:
    """Получить тег по идентификатору"""
    r = await repository.get(uuid.UUID(id))
    return await repository.model_from_orm(r) if r is not None else None


@api_file_tags_router.get("/for_graph/{id}")
async def get_file_tag_for_graph(
    id: str,
    repository: FileTagRepository = fastapi.Depends(FileTagRepositoryRequired),
) -> TagModelForGraph | None:
    """Получить тег для графа по идентификатору"""
    r = await repository.get_with_files(uuid.UUID(id))
    return await repository.model_from_orm_for_graph(r) if r is not None else None


@api_file_tags_router.get("")
async def get_file_tags(
    schema: FileTagFilterSchema = fastapi.Query(),
    repository: FileTagRepository = fastapi.Depends(FileTagRepositoryRequired),
) -> list[FileTagModel]:
    """Получить списоке тегов по фильтру"""
    return await repository.models_from_orm(await repository.values(filter=schema))


__all__ = ["api_file_tags_router"]
