import fastapi
from .database import DatabaseSessionRequired
from sqlalchemy.ext.asyncio import AsyncSession
from utils.service.depends import AuthPermissionRequired
from utils.service import AuthUserEnvrimoment, UserBasePermissions
from services.file import FileTagRepository, create_file_tag_repository


async def FileTagRepositoryRequired(
    db: AsyncSession = fastapi.Depends(DatabaseSessionRequired),
) -> FileTagRepository:
    return create_file_tag_repository(
        env=None,
        database=db,
    )


async def AdminFileTagRepositoryRequired(
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
) -> FileTagRepository:
    return create_file_tag_repository(
        env=env,
        database=db,
    )


__all__ = [
    "FileTagRepositoryRequired",
    "AdminFileTagRepositoryRequired",
]
