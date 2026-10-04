import os
import hashlib
import asyncio
import aiofiles.os
import mimetypes
from datetime import datetime, timezone
from uuid import UUID, uuid4
from abc import ABC, abstractmethod
from typing import Iterable
from models import UserOrmModel, TagOrmModel, FileOrmModel, FileContentOrmModel
from utils.sbz.datastuctures import *
from utils.service import AuthUserEnvrimoment, UserModel
from sqlalchemy import select, or_, and_, func, desc
from sqlalchemy.orm import joinedload, selectinload, lazyload
from sqlalchemy.ext.asyncio import AsyncSession
from settings import SETTING
from .tags import create_file_tag_repository
from .file_types import create_file_type_repository
from ...user import create_user_repository


class FileRepository(ABC):
    """Репозиторий файлов"""

    @abstractmethod
    async def get(self, id: UUID) -> FileOrmModel | None:
        """Получить информацию о файле"""

    @abstractmethod
    async def get_path(self, id: UUID) -> str | None:
        """Получить путь к файлу"""

    @abstractmethod
    async def values(self, schema: FileFilterSchema) -> list[FileOrmModel]:
        """Получить список файлов ао фильтру"""

    @abstractmethod
    async def create(
        self,
        schema: FileSchema,
        file: str,
        move: bool = True,
    ) -> FileOrmModel:
        """Создать новый файл"""

    @abstractmethod
    async def update(
        self,
        schema: FileSchema,
        file: str | None = None,
        move: bool = True,
    ) -> FileOrmModel:
        """Обновить существующий файл"""

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить имеющийся файл"""

    @abstractmethod
    async def model_from_orm(self, orm: FileOrmModel) -> FileModel:
        """Преобразовать в модель"""

    @abstractmethod
    async def models_from_orm(self, orm: list[FileOrmModel]) -> list[FileModel]:
        """Преобразовать в модель"""

    
    
class FileRepositoryImpl(FileRepository):
    def __init__(
        self,
        env: AuthUserEnvrimoment,
        database: AsyncSession,
    ):
        super().__init__()
        self.env = env
        self.db = database
        self.types = create_file_type_repository(
            env=env,
            database=database,
        )
        self.users = create_user_repository(
            env=env,
            database=database,
        )
        self.tags = create_file_tag_repository(
            env=env,
            database=database,
        )

    async def get(self, id: UUID) -> FileOrmModel | None:
        orm = await self.db.get(
            FileOrmModel,
            id,
            options=[
                selectinload(FileOrmModel.content),
                selectinload(FileOrmModel.tags),
                selectinload(FileOrmModel.type),
                selectinload(FileOrmModel.owner),
                # joinedload(FileOrmModel.last_edit_user),
            ],
        )
        return orm

    async def get_path(self, id: UUID) -> str | None:
        orm = await self.db.get(
            FileOrmModel, id, options=[joinedload(FileOrmModel.content)]
        )
        return os.path.join(SETTING.files_path, orm.content.path) if orm else None

    async def values(self, schema: FileFilterSchema) -> list[FileOrmModel]:
        user = await self.users.create(self.env.user) if self.env is not None else None
        offset = schema.offset if schema.offset is not None else 0
        limit = schema.limit if schema.limit is not None else 100
        tags: list[TagOrmModel] | None = None
        if schema.tag is not None or schema.keyword is not None:
            tags = []
            if schema.tag is not None:
                tags += await self.tags.values(FileTagFilterSchema(id=schema.tag))
            if schema.keyword is not None:
                tags += await self.tags.keywords(schema.keyword)

        result = list[FileOrmModel]()
        while len(result) < limit:
            schema.offset = offset
            schema.limit = limit - len(result)
            values = await self._values(schema, user=user)
            if len(values) == 0:
                break

            offset += len(values)
            if tags is not None:
                tags_id = set([tag.id for tag in tags])

                def tag_fiter(file: FileModel) -> bool:
                    file_tag_ids = set([tag.id for tag in file.tags])
                    return len(tags_id & file_tag_ids) > 0

                values = list(filter(tag_fiter, values))

            result += values

        return result

    async def create(
        self,
        schema: FileSchema,
        file: str,
        move: bool = True,
    ) -> FileOrmModel:
        user = await self.users.create(self.env.user)
        name = (
            schema.name.strip()
            if schema.name is not None
            else os.path.splitext(os.path.basename(file))[0].strip()
        )
        tags = (
            await self.tags.values(FileTagFilterSchema(id=schema.tags))
            if schema.tags is not None and len(schema.tags) > 0
            else []
        )
        tags += (
            await self.tags.keywords(schema.keywords)
            if schema.keywords is not None
            else []
        )
        content = await self._load_file_content(file, move=move)
        type = (
            await self.types.get(schema.type)
            if schema.type is not None
            else (
                await self.types.get_by_ext(content.extension)
                if schema.type_code is None
                else await self.types.get_by_code(schema.type_code)
            )
        )
        if type is None:
            raise ValueError("Не удалось определить тип файла", content.extension)

        dublicates = (
            (
                await self.db.execute(
                    select(FileOrmModel)
                    .where(
                        and_(
                            FileOrmModel.deleted == None,
                            FileOrmModel.content_id == content.id,
                            or_(
                                FileOrmModel.owner_id == user.id,
                                and_(
                                    FileOrmModel.is_public == True,
                                    func.lower(FileOrmModel.name) == name.lower(),
                                ),
                            ),
                        )
                    )
                    .order_by(desc(FileOrmModel.created))
                    .limit(1)
                )
            )
            .scalars()
            .all()
        )
        if len(dublicates) > 0:
            return dublicates[0]

        orm = FileOrmModel(
            id=schema.id if schema.id is not None else uuid4(),
            content_id=content.id,
            type=type,
            name=(
                schema.name.strip()
                if schema.name is not None
                else os.path.splitext(os.path.basename(file))[0].strip()
            ),
            description=(
                schema.description.strip() if schema.description is not None else ""
            ),
            is_public=schema.is_public,
            owner_id=user.id,
            # last_edit_user_id=user.internal_id,
            tags=tags,
        )

        self.db.add(orm)

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(orm.content)
        await self.db.refresh(orm)
        return await self.get(orm.id)

    async def update(
        self,
        schema: FileSchema,
        file: str | None = None,
        move: bool = True,
    ) -> FileOrmModel:
        orm = (
            await self.db.get(
                FileOrmModel,
                schema.id,
                options=[
                    joinedload(FileOrmModel.content),
                    joinedload(FileOrmModel.tags),
                    joinedload(FileOrmModel.type),
                    joinedload(FileOrmModel.owner),
                    # joinedload(FileOrmModel.last_edit_user),
                ],
            )
            if schema.id is not None
            else None
        )
        if orm is None:
            if file is not None:
                return await self.create(schema, file, move)
            raise ValueError(f"File not found", schema)

        if file is not None:
            content_orm = await self._load_file_content(file, move=move)
            orm.content_id = content_orm.id

        if schema.type is not None:
            orm.type_id = schema.type

        if schema.type_code is not None:
            type = await self.types.get_by_code(schema.type_code)
            if type is None:
                raise ValueError(f"Не удалось найти тип {schema.type_code}")
            orm.type = type

        if schema.name is not None:
            orm.name = schema.name.strip()

        if schema.description is not None:
            orm.description = schema.description.strip()

        if schema.tags is not None or schema.keywords is not None:
            tags = (
                await self.tags.values(FileTagFilterSchema(id=schema.tags))
                if schema.tags is not None
                else []
            )
            if schema.keywords is not None:
                tags += await self.tags.keywords(schema.keywords)

            orm.tags = tags

        orm.deleted = None

        await self.db.flush()
        await self.db.commit()
        return await self.get(orm.id)

    async def delete(self, id: UUID) -> None:
        orm = await self.db.get(FileOrmModel, id)
        if orm is not None:
            orm.deleted = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.flush()
            await self.db.commit()

    async def _values(
        self, schema: FileFilterSchema, user: UserOrmModel | None = None
    ) -> list[FileOrmModel]:
        file_query = select(FileOrmModel)
        file_query = file_query.options(
            selectinload(FileOrmModel.content),
            selectinload(FileOrmModel.tags),
            selectinload(FileOrmModel.type),
            selectinload(FileOrmModel.owner),
            # joinedload(FileOrmModel.last_edit_user),
        )

        if schema.id is not None:
            file_query = file_query.where(FileOrmModel.id.in_(schema.id))

        schema.owner_type = (
            schema.owner_type if schema.owner_type is not None else "common"
        )

        if schema.owner_type is not None:
            if schema.owner_type == "my" and user is not None:
                file_query = file_query.where(
                    and_(
                        FileOrmModel.owner_id == user.id,
                        FileOrmModel.is_public == False,
                    )
                )
            elif schema.owner_type == "all" and user is not None:
                file_query = file_query.where(
                    or_(
                        FileOrmModel.is_public == True,
                        FileOrmModel.owner_id == user.id,
                    )
                )
            else:
                file_query = file_query.where(FileOrmModel.is_public == True)

        if schema.name is not None:
            file_query = file_query.where(
                (func.lower(FileOrmModel.name).contains(schema.name[0].lower().strip()))
                if len(schema.name) == 1
                else (
                    or_(
                        *[
                            func.lower(FileOrmModel.name).contains(name.lower().strip())
                            for name in schema.name
                        ]
                    )
                )
            )

        if schema.description is not None:
            file_query = file_query.where(
                (
                    func.lower(FileOrmModel.description).contains(
                        schema.description[0].lower().strip()
                    )
                )
                if len(schema.description) == 1
                else (
                    or_(
                        *[
                            func.lower(FileOrmModel.description).contains(
                                description.lower().strip()
                            )
                            for description in schema.description
                        ]
                    )
                )
            )

        if schema.type is not None:
            file_query = file_query.where(FileOrmModel.type_id.in_(schema.type))

        if schema.type_code is not None:
            types = [
                type.id
                for type in [
                    await self.types.get_by_code(code) for code in schema.type_code
                ]
                if type is not None
            ]
            file_query = file_query.where(FileOrmModel.type_id.in_(types))

        if schema.enabled is not None:
            if schema.enabled:
                file_query = file_query.where(FileOrmModel.deleted == None)
            else:
                file_query = file_query.where(FileOrmModel.deleted != None)

        if schema.created_begin is not None:
            file_query = file_query.where(
                FileOrmModel.created >= schema.created_begin.replace(tzinfo=None)
            )

        if schema.created_end is not None:
            file_query = file_query.where(
                FileOrmModel.created < schema.created_end.replace(tzinfo=None)
            )

        if schema.updated_begin is not None:
            file_query = file_query.where(
                FileOrmModel.modified >= schema.updated_begin.replace(tzinfo=None)
            )

        if schema.updated_end is not None:
            file_query = file_query.where(
                FileOrmModel.modified < schema.updated_end.replace(tzinfo=None)
            )

        if schema.owner is not None: 
            file_query = file_query.where(FileOrmModel.owner.has(
                UserOrmModel.user_id.in_(schema.owner)
            ))
        file_query = file_query.order_by(desc(FileOrmModel.created))
        values: list[FileOrmModel] = list(
            (
                await self.db.execute(
                    file_query.offset(
                        schema.offset if schema.offset is not None else 0
                    ).limit(schema.limit if schema.limit is not None else 100)
                )
            )
            .scalars()
            .all()
        )

        if schema.extension is not None:
            values = list(
                filter(lambda f: f.content.extension in schema.extension, values)
            )

        if schema.mimetype is not None:
            values = list(
                filter(lambda f: f.content.mimetype in schema.mimetype, values)
            )

        return values

    async def _load_file_content(
        self,
        file: str,
        move: bool = True,
    ) -> FileContentOrmModel:
        size = await aiofiles.os.path.getsize(file)
        md5, sha256 = await self._calculate_sum(file)

        orm = (
            (
                await self.db.execute(
                    select(FileContentOrmModel)
                    .where(FileContentOrmModel.deleted == None)
                    .where(
                        and_(
                            FileContentOrmModel.size == size,
                            FileContentOrmModel.md5_checksum == md5,
                            FileContentOrmModel.sha256_checksum == sha256,
                        )
                    )
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )
        if orm is not None and await aiofiles.os.path.exists(
            os.path.join(SETTING.files_path, orm.path)
        ):
            return orm

        else:
            name, ext = os.path.splitext(os.path.basename(file))
            mimetype = mimetypes.guess_extension(ext)
            if mimetype is None:
                mimetypes.guess_type(file)

            if mimetype is None:
                mimetype = "application/octet-stream"

            id = uuid4()
            now = datetime.now(timezone.utc)
            relative = os.path.join(
                str(now.year),
                str(now.month),
                str(now.day),
                str(id) + ext,
            )
            new_path = os.path.abspath(os.path.join(SETTING.files_path, relative))

            orm = FileContentOrmModel(
                id=id,
                path=relative,
                mimetype=mimetype,
                extension=ext,
                size=size,
                md5_checksum=md5,
                sha256_checksum=sha256,
            )
            self.db.add(orm)

            dir = os.path.dirname(new_path)
            if not await aiofiles.os.path.exists(dir):
                await aiofiles.os.makedirs(dir, exist_ok=True)

            async with aiofiles.open(file, "rb") as src:
                async with aiofiles.open(new_path, "wb") as dst:
                    while True:
                        data = await src.read(4096)
                        if len(data) > 0:
                            await dst.write(data)
                        else:
                            break

            if move:
                await aiofiles.os.remove(file)
                # await aiofiles.os.rename(file, new_path)
            # else:
            #     async with aiofiles.open(file, "rb") as src:
            #         async with aiofiles.open(new_path, "wb") as dst:
            #             while True:
            #                 data = await src.read(4096)
            #                 if len(data) > 0:
            #                     await dst.write(data)
            #                 else:
            #                     break

            try:
                await self.db.flush()
                await self.db.commit()
            except Exception as ex:
                aiofiles.os.remove(new_path)
                raise ex

            return orm

    async def _calculate_sum(self, path: str) -> tuple[str, str]:  # [md5, sha256]
        async with aiofiles.open(path, "rb") as f:
            md5 = hashlib.md5()
            sha256 = hashlib.sha256()

            while True:
                data = await f.read()
                if len(data) == 0:
                    break

                md5.update(data)
                sha256.update(data)

            return md5.hexdigest(), sha256.hexdigest()

    async def model_from_orm(self, orm: FileOrmModel) -> FileModel:
        return FileModel(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            type=await self.types.model_from_orm(orm.type),
            mimetype=orm.content.mimetype,
            extension=orm.content.extension,
            size=orm.content.size,
            md5_checksum=orm.content.md5_checksum,
            sha256_checksum=orm.content.sha256_checksum,
            tags=await self.tags.models_from_orm(orm.tags),
            is_public=orm.is_public,
            owner=UserModel(
                id=orm.owner.user_id,
                provider=orm.owner.user_provider,
                username=orm.owner.username,
                first_name=orm.owner.first_name,
                last_name=orm.owner.last_name,
                patronymic=orm.owner.patronymic,
            ),
            enabled=orm.enabled,
            created=orm.created,
            modified=orm.modified,
            deleted=orm.deleted,
        )

    async def models_from_orm(self, orm: list[FileOrmModel]) -> list[FileModel]:
        return [await self.model_from_orm(item) for item in orm]

                
def create_file_repository(
    env: AuthUserEnvrimoment,
    database: AsyncSession,
) -> FileRepository:
    return FileRepositoryImpl(
        env=env,
        database=database,
    )


__all__ = [
    "FileRepository",
    "create_file_repository",
    
]
