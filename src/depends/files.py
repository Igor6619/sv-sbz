import uuid
import fastapi
from schemas import *
from typing import Optional, Union
from .database import DatabaseSessionRequired
from sqlalchemy.ext.asyncio import AsyncSession
from utils.sbz.datastuctures.schemas import FileSchema, FileFilterSchema
from utils.service.depends import AuthEnvrimomentOrNone, AuthPermissionsOrNone, AuthPermissionRequired
from utils.service import AuthUserEnvrimoment, UserBasePermissions, PydanticHelper
from services.file import FileRepository, create_file_repository


async def FileSchemaAsForm(
    id: Optional[str] = fastapi.Form(default=None),
    type: Optional[str] = fastapi.Form(default=None),
    type_code: Optional[str] = fastapi.Form(default=None),
    file_type: Optional[str] = fastapi.Form(default=None),
    file_type_code: Optional[str] = fastapi.Form(default=None),
    name: Optional[str] = fastapi.Form(default=None),
    description: Optional[str] = fastapi.Form(default=None),
    mimetype: Optional[str] = fastapi.Form(default=None),
    is_public: Optional[bool] = fastapi.Form(default=True),
    keywords: Optional[list[str]] = fastapi.Form(default=None),
    tags: Optional[list[Union[str, uuid.UUID, object, dict]]] = fastapi.Form(
        default=None
    ),
    disciplines: Optional[list[Union[str, uuid.UUID, object, dict]]] = fastapi.Form(
        default=None
    ),
) -> FileSchema:
    all_tags = []
    if tags is not None:
        all_tags += tags
    if disciplines is not None:
        all_tags += disciplines

    if all_tags is not None: 
        all_tags = [i for i in all_tags if len(i) > 0]
        
    if keywords is not None: 
        keywords = [i for i in keywords if len(i) > 0]
    
    return FileSchema(
        id=id,
        type=type if type is not None else file_type,
        type_code=type_code if type_code is not None else file_type_code,
        name=name,
        description=description,
        mimetype=mimetype,
        is_public=is_public,
        tags=all_tags,
        keywords=keywords,
    )


async def FileSearchSchemaAsForm(
    search_type: Optional[str] = fastapi.Query(default=None),
    value: Optional[str] = fastapi.Query(default=None),
    name: Optional[str] = fastapi.Query(default=None),
    description: Optional[str] = fastapi.Query(default=None),
    mimetype: Optional[str] = fastapi.Query(default=None),
    keywords: Optional[list[str]] = fastapi.Query(default=None),
    type: Optional[str | list[str]] = fastapi.Query(default=None),
    tags: Optional[list[Union[str, uuid.UUID]]] = fastapi.Query(default=None),
    equipment: Optional[list[Union[str, uuid.UUID]]] = fastapi.Query(default=None),
    discipline: Optional[list[Union[str, uuid.UUID]]] = fastapi.Query(default=None),
    equipments: Optional[list[Union[str, uuid.UUID]]] = fastapi.Query(default=None),
    disciplines: Optional[list[Union[str, uuid.UUID]]] = fastapi.Query(default=None),
) -> FileFilterSchema:
    all_tags = []
    
    if tags is not None: 
        all_tags += tags
    
    if equipment is not None:
        all_tags += equipment
        
    if discipline is not None:
        all_tags += discipline
        
    if equipments is not None:
        all_tags += equipments
        
    if disciplines is not None:
        all_tags += disciplines
    
    if len(all_tags) == 0: 
        all_tags = None

    if search_type == FileSearchType.Name:
        name = value

    elif search_type == FileSearchType.Description:
        description = value

    elif search_type == FileSearchType.Keywords:
        keywords = value

    elif search_type == FileSearchType.Content:
        pass
    
    name = PydanticHelper.validators.str_list(name)
    description = PydanticHelper.validators.str_list(description)
    keywords = PydanticHelper.validators.str_list(keywords)
    all_tags = PydanticHelper.validators.uuid_list(all_tags)

    return FileFilterSchema(
        type=type,
        name=name,
        description=description,
        mimetype=mimetype,
        is_public=True,
        tag=all_tags,
        keyword=keywords,
    )


async def FileRepositoryRequired(
    env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
    db: AsyncSession = fastapi.Depends(DatabaseSessionRequired),
) -> FileRepository:
    return create_file_repository(
        env=env,
        database=db,
    )


async def AdminFileRepositoryRequired(
    env: AuthUserEnvrimoment = fastapi.Depends(
        AuthPermissionRequired(
            [
                UserBasePermissions.Admin,
                UserBasePermissions.Metodis,
                UserBasePermissions.Official,
                UserBasePermissions.Teacher,
            ]
        )
    ),
    db: AsyncSession = fastapi.Depends(DatabaseSessionRequired),
) -> FileRepository:
    return create_file_repository(
        env=env,
        database=db,
    )


async def IsFileRepositoryAdmin(
    env: AuthUserEnvrimoment = fastapi.Depends(
        AuthPermissionsOrNone(
            [
                UserBasePermissions.Admin,
                UserBasePermissions.Metodis,
                UserBasePermissions.Official,
                UserBasePermissions.Teacher,
            ]
        )
    ),
) -> bool:
    return env is not None


__all__ = [
    "FileSchemaAsForm",
    "FileSearchSchemaAsForm",
    "FileRepositoryRequired",
    "AdminFileRepositoryRequired",
    "IsFileRepositoryAdmin",
]
