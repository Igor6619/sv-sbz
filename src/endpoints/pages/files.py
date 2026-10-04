import os
import uuid
import fastapi
import tempfile
import aiofiles
from schemas import *
from typing import Union, Optional
from datetime import datetime
from models import FileTypeCode
from fastapi.templating import Jinja2Templates
from depends import *
from services.file import FileRepository, FileTypeRepository, FileTagRepository
from services.search_query import SearchQueryRepository
from utils.sbz.datastuctures.models import FileModel, FileTagModel
from utils.sbz.datastuctures.schemas import (
    FileSchema,
    FileFilterSchema,
    FileTagFilterSchema,
)
from utils.service.authentication import AuthUserEnvrimoment
from utils.service.depends import AuthEnvrimomentOrNone
from settings import SETTING


files_router = fastapi.routing.APIRouter()
templates = Jinja2Templates(
    directory=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    )
)


@files_router.get("")
async def search_files_page(
    request: fastapi.Request,
    search_type: Optional[str] = fastapi.Query(default=None),
    value: Optional[str] = fastapi.Query(default=None),
    type: Optional[str | list[str]] = fastapi.Query(default=None),
    equipment: Optional[list[Union[str, uuid.UUID]]] = fastapi.Query(default=None),
    discipline: Optional[list[Union[str, uuid.UUID]]] = fastapi.Query(default=None),
    schema: FileFilterSchema = fastapi.Depends(FileSearchSchemaAsForm),
    is_adm: bool = fastapi.Depends(IsFileRepositoryAdmin),
    env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
    tags: FileTagRepository = fastapi.Depends(FileTagRepositoryRequired),
    types: FileTypeRepository = fastapi.Depends(FileTypeRepositoryRequired),
    files: FileRepository = fastapi.Depends(FileRepositoryRequired),
    search_queries: SearchQueryRepository = fastapi.Depends(SearchQueryRepositoryRequired),
):
    _files = await files.values(schema=schema)
    if value:
        results_count = len(_files)
        await search_queries.add(
            SearchQueryModel(
                value=value,
                results_count=results_count
            )
        )
    equipments = await tags.get_by_code("equipments")
    disciplines = await tags.get_by_code("disciplines")

    other_tags = await tags.values(
        FileTagFilterSchema(exclude_code=["disciplines", "equipments"], keyword=False)
    )

    search_types = [
        FileNameSearch(value=""),
        FileKeywordsSearch(value=[]),
        FileDescriptionSearch(value=""),
        FileContentSearch(value=""),
    ]

    context = {
        "request": request,
        "is_file_adm": is_adm,
        "user": env.user if env is not None else None,
        "files": _files,
        "file_types": await types.values(),
        "main_tags": other_tags if other_tags is not None else [],
        "equipments": equipments.children if equipments is not None else [],
        "disciplines": disciplines.children if disciplines is not None else [],
        "types_search": search_types,
        "filters": {
            "type": type[0] if type is not None else None,
            "value": value,
            "search_type": search_type,
            "equipment": equipment[0] if equipment is not None else None,
            "discipline": discipline[0] if discipline is not None else None,
        },
        "omni_url": SETTING.omni_url
    }
    return templates.TemplateResponse("files/search.html", context=context)


@files_router.get("/upload")
async def upload_file_page(
    request: fastapi.Request,
    env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
    tags: FileTagRepository = fastapi.Depends(FileTagRepositoryRequired),
    types: FileTypeRepository = fastapi.Depends(FileTypeRepositoryRequired),
):
    disciplines = await tags.get_by_code("disciplines")
    other_tags = await tags.values(
        FileTagFilterSchema(exclude_code="disciplines", keyword=False)
    )

    context = {
        "request": request,
        "user": env.user if env is not None else None,
        "file_types": await types.values(),
        "main_tags": other_tags if other_tags is not None else [],
        "disciplines": disciplines.children if disciplines is not None else [],
    }
    return templates.TemplateResponse("files/upload.html", context=context)


@files_router.post("/upload")
async def upload_file_page(
    schema: FileSchema = fastapi.Depends(FileSchemaAsForm),
    file: fastapi.UploadFile = fastapi.File(),
    repository: FileRepository = fastapi.Depends(AdminFileRepositoryRequired),
):
    CHUNK_SIZE = 1024 * 1024 * 10
    name, ext = os.path.splitext(file.filename)
    if schema.name is None:
        schema.name = name

    path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + ext)
    async with aiofiles.open(path, "wb") as dst:
        while True:
            data = file.file.read(CHUNK_SIZE)
            if len(data) > 0:
                await dst.write(data)
            else:
                break
    await repository.create(
        schema=schema,
        file=path,
        move=True,
    )

    return fastapi.responses.RedirectResponse("/", status_code=303)


@files_router.get("/update")
async def update_file_page(
    request: fastapi.Request,
    id: str | None = fastapi.Query(default=None),
    env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired),
    tags: FileTagRepository = fastapi.Depends(FileTagRepositoryRequired),
    types: FileTypeRepository = fastapi.Depends(FileTypeRepositoryRequired),
):
    if id is None:
        return fastapi.responses.RedirectResponse("/")

    file = await repository.get(uuid.UUID(id))
    if file is None:
        return fastapi.Response(status_code=404)

    disciplines = await tags.get_by_code("disciplines")
    other_tags = await tags.values(
        FileTagFilterSchema(exclude_code="disciplines", keyword=False)
    )

    def to_line_tags(tags: list[FileTagModel]) -> list[FileTagModel]:
        result = []
        try:
            result = list(tags)
            for tag in tags:
                result += to_line_tags(tag.children)
        except Exception:
            pass
        return result

    file_all_tags = to_line_tags(file.tags)
    selected_tags = [
        tag.id for tag in list(filter(lambda k: not k.keyword, file_all_tags))
    ]
    selected_keywords = [
        key.name for key in list(filter(lambda k: k.keyword, file_all_tags))
    ]

    context = {
        "request": request,
        "user": env.user if env is not None else None,
        "file": await repository.get(uuid.UUID(id)),
        "selected_tags": selected_tags,
        "selected_keywords": ",".join(selected_keywords),
        "file_types": await types.values(),
        "main_tags": other_tags if other_tags is not None else [],
        "disciplines": disciplines.children if disciplines is not None else [],
    }
    return templates.TemplateResponse("files/update.html", context=context)


@files_router.post("/update")
async def update_file_page(
    request: fastapi.Request,
    id: str = fastapi.Query(),
    schema: FileSchema = fastapi.Depends(FileSchemaAsForm),
    file: fastapi.UploadFile | None = fastapi.File(default=None),
    repository: FileRepository = fastapi.Depends(AdminFileRepositoryRequired),
):
    schema.id = id
    path: str = None

    if file is not None and file.size > 0:
        name, ext = os.path.splitext(file.filename)
        if schema.name is None:
            schema.name = name

        path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + ext)
        async with aiofiles.open(path, "wb") as dst:
            while True:
                data = file.file.read(4096)
                if len(data) > 0:
                    await dst.write(data)
                else:
                    break

    await repository.update(
        schema=schema,
        file=path,
        move=True,
    )

    return fastapi.responses.RedirectResponse("/", status_code=303)


###############  START FILTERS ###################
def format_date(value, format="%d.%m.%Y"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value


def count_show(value):
    return "(нет данных) "


def get_file_ext(file: FileModel) -> str:
    return file.extension


def is_360(file: FileModel) -> bool:
    return file.type.code in [FileTypeCode.FRKP.value, FileTypeCode.VIDEO_360.value]


def to_line_tags(file) -> list:
    def to_lines(tags) -> list:
        result = list(tags)
        for tag in tags:
            try:
                result += to_lines(tag.children)
            except Exception as ex:
                pass
        return result

    try:
        return to_lines(file.tags)
    except Exception as ex:
        pass
    return []


templates.env.filters["format_date"] = format_date
templates.env.filters["count_show"] = count_show
templates.env.filters["get_file_ext"] = get_file_ext
templates.env.filters["is_360"] = is_360
templates.env.filters["to_line_tags"] = to_line_tags

__all__ = ["files_router"]
