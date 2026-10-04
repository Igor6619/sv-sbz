import logging
import os
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    Query,
    Form,
)
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from pydantic.v1 import UUID4
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.util import await_only
from starlette.responses import RedirectResponse

from services.database.db_helper import db_helper
from user.utils import is_login
from .crud import create_file, get_file, get_files, update_file, delete_file
from .log import lprint, logger
from utils.file import get_path_for_file_save
from utils.file import get_media_type
import file.schemas as sch
from file.schemas import FileCreate as FileCreateSch
from typing import Union, Optional, List
from . import crud, models
from sqlalchemy.ext.asyncio.session import AsyncSession
from user.schemas import User
from .utils import MainTags
from uuid import UUID
from .templates import templates
from .utils import TYPE_SEARCH, iter_file
from urllib.parse import quote

router = APIRouter()


@router.get("/")
async def file_html(request: Request, db=Depends(db_helper.session_getter)):

    main_tags = []
    for main_tag_name in (MainTags.APPARATS,):
        main_tag = await crud.get_tag_by_name(db, main_tag_name)
        tags = await crud.get_all_descendants(db, main_tag.id)
        tags = [
            Tag(id=tag.id, name=tag.name, parent_id=tag.parent_id).model_dump()
            for tag in tags
        ]
        main_tags.append((main_tag_name, Tag.build_tree(tags, main_tag.id)))

    main_tag = await crud.get_tag_by_name(db, MainTags.DISCIPLINES)
    tags = await crud.get_all_descendants(db, main_tag.id)
    tags = [
        Tag(id=tag.id, name=tag.name, parent_id=tag.parent_id).model_dump()
        for tag in tags
    ]
    disciplines = Tag.build_tree(tags, main_tag.id)[0]["children"]
    print(disciplines)
    file_types = await crud.get_all_model(db, models.FileTypeOrmModel)
    context = {
        "request": request,
        "main_tags": main_tags,
        "disciplines": disciplines,
        "file_types": file_types,
    }

    return templates.TemplateResponse("file_add.html", context)


@router.get("/test_search")
async def file_html_search(
    request: Request,
    filter_name: str = Query(""),
    filter_search_type: str = Query(""),
    filter_file_type: str = Query(""),
    filter_discipline: str = Query(""),
    filter_apparats: str = Query(""),
    db=Depends(db_helper.session_getter),
):

    discipline_main_tag: models.TagOrmModel = await crud.get_tag_by_name(
        db, MainTags.DISCIPLINES
    )
    await db.refresh(discipline_main_tag, ["children"])

    file_type_main_tag: list[models.FileTypeOrmModel] = (
        (await db.execute(select(models.FileTypeOrmModel))).scalars().all()
    )

    apparats_main_tag = await crud.get_tag_by_name(db, MainTags.APPARATS)
    apparats_tags = await crud.get_all_descendants(db, apparats_main_tag.id)
    apparats_tags = [
        Tag(id=tag.id, name=tag.name, parent_id=tag.parent_id).model_dump()
        for tag in apparats_tags
    ]
    apparats = Tag.build_tree(apparats_tags, apparats_main_tag.id)[0]
    tags_pk = []
    if filter_apparats:
        tags_pk.append(UUID(filter_apparats))
    if filter_discipline:
        tags_pk.append(UUID(filter_discipline))

    files = await crud.get_files_by_filters(
        db, filter_search_type, filter_name, filter_file_type, tags_pk
    )

    print("files")
    print(files)

    filters = {
        "name": filter_name,
        "search_type": filter_search_type,
        "file_type": filter_file_type,
        "discipline": filter_discipline,
        "apparats": filter_apparats,
    }

    context = {
        "request": request,
        "types_search": TYPE_SEARCH,
        "disciplines": discipline_main_tag.children,
        "file_types": file_type_main_tag,
        "apparats": apparats,
        "files": files,
        "filters": filters,
    }
    return templates.TemplateResponse("file_search.html", context)


@router.post("/test_add_file")
async def test_add_file(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    is_private: bool = Form(False),
    file_type: str = Form(...),
    file: UploadFile = File(...),
    tags: List[str] = Form(default_factory=list),
    keywords: str = Form(...),
    # user: User = Depends(is_login),
    db=Depends(db_helper.session_getter),
):
    mime_type: str = file.content_type
    owner_pk = 1  # user.id
    keywords: List[str] = [
        keyword.lower().strip() for keyword in keywords.split(",") if keyword
    ]

    main_keyword_tag: models.TagOrmModel = await crud.get_tag_by_name(db, MainTags.KEYWORDS)
    for keyword in keywords:
        db_tag = await crud.get_tag_by_name(db, keyword)
        if not db_tag:
            tag = sch.TagCreate(name=keyword, parent_id=main_keyword_tag.id)
            db_tag = await crud.create_tag(db, tag)
        tags.append(db_tag.id)

    path = get_path_for_file_save(file.filename)

    async with aiofiles.open(path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    db_file: models.FileOrmModel = models.FileOrmModel(
        name=name,
        path=path,
        description=description,
        owner_pk=owner_pk,
        file_type_pk=UUID(file_type),
        mime_type=mime_type,
        is_private=is_private,
    )

    db.add(db_file)
    db_file.tags = await crud.get_list_by_pks(db, models.TagOrmModel, tags)
    await db.commit()
    await db.refresh(db_file)

    return RedirectResponse(url=request.url_for("file_html_search"), status_code=303)


@router.get("/download_stream/{file_id}")
async def download_stream(
    file_id: UUID,
    db=Depends(db_helper.session_getter),
):
    file: models.FileOrmModel = await crud.get_file(db, file_id)

    if not os.path.exists(file.path):
        raise HTTPException(status_code=404, detail="File not found on server")

    file_name: str = os.path.basename(file.path)
    media_type = get_media_type(file_name)

    # Браузер не будет пытаться открыть файл, просто скачает
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(file_name)}"
    }

    logger.log(
        logging.DEBUG,
        f"Отправка файла. Наименование: {file_name}, MIME:{media_type}, PATH: {file.path}",
    )

    return StreamingResponse(
        iter_file(file.path), media_type=media_type, headers=headers
    )


@router.get("/download/{file_id}/")
async def download_file(
    file_id: UUID,
    db=Depends(db_helper.session_getter),
):
    file: models.FileOrmModel = await crud.get_file(db, file_id)

    if not os.path.exists(file.path):
        raise HTTPException(status_code=404, detail="File not found on server")

    file_name: str = os.path.basename(file.path)

    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(file_name)}"
    }

    logger.log(
        logging.DEBUG,
        f"Отправка файла. Наименование: {file_name}, MIME:{file.mimetype}, PATH: {file.path}",
    )

    return FileResponse(
        file.path, filename=file_name, media_type=file.mimetype, headers=headers
    )


####################################################

from .schemas import File as FileSch
from .schemas import FileUpdate as FileUpdateSch
import aiofiles


@router.post(
    "/files/",
    response_model=FileSch,
)
async def create_file_end(
    request: Request,
    file: UploadFile = File(...),
    file_data: FileCreateSch = Depends(FileCreateSch.as_form),
    db: AsyncSession = Depends(db_helper.session_getter),
):

    lprint("file_data")
    lprint(type(file_data))
    lprint(file_data)

    lprint("create_file_end")
    user: int = 1  # request.user_sso.id

    file_path = get_path_for_file_save(file.filename)
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(await file.read())

    db_file = await create_file(db, file_data, user)
    db_file.path = file_path
    await db.commit()
    await db.refresh(db_file, attribute_names=["type"])
    lprint(db_file)
    return db_file


@router.get("/files/{file_uuid}", response_model=FileSch)
async def read_file(
    file_uuid: UUID, db: AsyncSession = Depends(db_helper.session_getter)
):
    db_file = await get_file(db, file_uuid)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file


@router.get("/files/", response_model=list[FileSch])
async def read_files(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(db_helper.session_getter),
):
    files = await get_files(db, skip, limit)
    return files


@router.put("/files/{file_uuid}", response_model=FileSch)
async def update_file_endpoint(
    file_uuid: UUID,
    file_update: FileUpdateSch,
    db: AsyncSession = Depends(db_helper.session_getter),
):
    db_file = await update_file(db, file_uuid, file_update)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file


@router.delete("/files/{file_uuid}")
async def delete_file_endpoint(
    file_uuid: UUID, db: AsyncSession = Depends(db_helper.session_getter)
):
    db_file = await get_file(db, file_uuid)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    await delete_file(db, file_uuid)
    os.remove(db_file.path)
    return {"detail": "File deleted"}


########################### START TAGTREE  #######################

from .schemas import Tag, TagCreate, TagUpdate
from .crud import (
    create_tag,
    get_tags,
    update_tag,
    delete_tag,
    get_all_descendants,
    create_tags_from_file,
)

from uuid import UUID


@router.post("/tags/", response_model=Tag)
async def create_tag_endpoint(
    tag: TagCreate, db: AsyncSession = Depends(db_helper.session_getter)
):
    return await create_tag(db, tag)


@router.get("/tags/{tag_id}")
async def read_tag(tag_id: UUID, db: AsyncSession = Depends(db_helper.session_getter)):
    tags = await get_all_descendants(db, tag_id)

    tags = [
        Tag(id=tag.id, name=tag.name, parent_id=tag.parent_id).model_dump()
        for tag in tags
    ]

    return Tag.build_tree(tags, tag_id)


@router.get("/tags/", response_model=List[Tag])
async def read_tags(db: AsyncSession = Depends(db_helper.session_getter)):

    res = await get_tags(db)

    return res


@router.put("/tags/{tag_id}", response_model=Tag)
async def update_tag_endpoint(
    tag_id: UUID,
    tag_update: TagUpdate,
    db: AsyncSession = Depends(db_helper.session_getter),
):
    return await update_tag(db, tag_id, tag_update)


@router.delete("/tags/{tag_id}", response_model=dict)
async def delete_tag_endpoint(
    tag_id: UUID, db: AsyncSession = Depends(db_helper.session_getter)
):
    return await delete_tag(db, tag_id)


@router.post("/load_tags_from_file/")
async def create_file_end(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(db_helper.session_getter),
):
    import json

    tags = json.load(file.file)

    for tag in tags:
        _ = await create_tags_from_file(db, tag)

    return tags


########################### END TAGTREE  #########################


################## API ######################
from .models import FileOrmModel as FileModel


@router.get('/get_files_api')
async def get_files(request: Request, db=Depends(db_helper.session_getter)):
    # Получаем все записи
    stmt = select(FileModel).options(selectinload(FileModel.type))
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [item.__dict__ for item in items]
################## END API ##################
