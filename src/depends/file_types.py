import fastapi
from .database import DatabaseSessionRequired
from sqlalchemy.ext.asyncio import AsyncSession
from utils.service.depends import AuthPermissionRequired
from utils.service import AuthUserEnvrimoment, UserBasePermissions
from services.file import FileTypeRepository, create_file_type_repository


async def FileTypeRepositoryRequired(
    db: AsyncSession = fastapi.Depends(DatabaseSessionRequired),
) -> FileTypeRepository:
    return create_file_type_repository(
        env=None,
        database=db,
    )


async def AdminFileTypeRepositoryRequired(
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
) -> FileTypeRepository:
    return create_file_type_repository(
        env=env,
        database=db,
    )


__all__ = [
    "FileTypeRepositoryRequired",
    "AdminFileTypeRepositoryRequired",
]
