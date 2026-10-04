from uuid import UUID, uuid4
from abc import ABC, abstractmethod
from models import FileTypeOrmModel
from utils.sbz.datastuctures import *
from utils.service import AuthUserEnvrimoment
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class FileTypeRepository(ABC):
    """Репозиторий типов файлов"""

    @abstractmethod
    async def get(self, id: UUID) -> FileTypeOrmModel | None:
        """Получить информацию о типе файла"""

    @abstractmethod
    async def get_by_ext(self, value: str) -> FileTypeOrmModel | None:
        """Получить тип файла по расширению файла"""
        
    @abstractmethod
    async def get_by_code(self, value: str) -> FileTypeOrmModel | None: 
        """Получить тип файла по коду типа"""

    @abstractmethod
    async def values(self) -> list[FileTypeModel]:
        """Получить список типов файлов"""

    @abstractmethod
    async def create(self, schema: FileTypeSchema) -> FileTypeOrmModel:
        """Создать тип файла"""

    @abstractmethod
    async def update(self, schema: FileTypeSchema) -> FileTypeOrmModel:
        """Обновить тип файла"""

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить тип файла"""

    @abstractmethod
    async def model_from_orm(self, orm: FileTypeOrmModel) -> FileTypeModel:
        """Преобразовать в модель"""

    @abstractmethod
    async def models_from_orm(self, orm: list[FileTypeOrmModel]) -> list[FileTypeModel]:
        """Преобразовать в модель"""


class FileTypeRepositoryImpl(FileTypeRepository):
    def __init__(
        self,
        env: AuthUserEnvrimoment,
        database: AsyncSession,
    ):
        super().__init__()
        self.env = env
        self.db = database

    async def get(self, id: UUID) -> FileTypeOrmModel | None:
        return await self.db.get(FileTypeOrmModel, id)

    async def get_by_ext(self, value: str) -> FileTypeOrmModel | None:
        types = await self.values()
        for type in types:
            if type.extensions is not None and value in type.extensions:
                return type

        return next((t for t in types if t.is_default), None)
    
    async def get_by_code(self, value: str) -> FileTypeOrmModel | None: 
        for type in await self.values():
            if type.code is not None and type.code == value:
                return type
        
        return None

    async def values(self) -> list[FileTypeOrmModel]:
        return list((await self.db.execute(select(FileTypeOrmModel).order_by(FileTypeOrmModel.created))).scalars().all())

    async def create(self, schema: FileTypeSchema) -> FileTypeOrmModel:
        if schema.name is None:
            raise ValueError("Name is required")

        if schema.id is None:
            schema.id = uuid4()

        value = FileTypeOrmModel(
            id=schema.id,
            name=schema.name,
            code=schema.code,
            extensions=schema.extensions,
            is_default=schema.default,
        )
        self.db.add(value)
        await self.db.flush()
        await self.db.commit()

        return value

    async def update(self, schema: FileTypeSchema) -> FileTypeOrmModel:
        if schema.id is None:
            raise ValueError("Id is required")

        if schema.name is None:
            raise ValueError("Name is required")

        value = await self.db.get(FileTypeOrmModel, schema.id)
        if value is None:
            raise ValueError("File type not found")

        value.name = schema.name
        value.code = schema.code
        value.is_default = schema.default
        value.extensions = (
            schema.extensions if schema.extensions is not None else value.extensions
        )
        value.deleted = None

        await self.db.flush()
        await self.db.commit()
        return value

    async def delete(self, id: UUID) -> None:
        value = await self.db.get(FileTypeOrmModel, id)
        if value is None:
            raise ValueError("File type not found")

        await self.db.delete(value)
        await self.db.commit()

    async def model_from_orm(self, orm: FileTypeOrmModel) -> FileTypeModel:
        return FileTypeModel(
            id=orm.id,
            name=orm.name,
            code=orm.code,
            extensions=orm.extensions if orm.extensions is not None else [],
            default=orm.is_default,
            created=orm.created,
            modified=orm.modified,
            deleted=orm.deleted,
            enabled=orm.enabled,
        )

        # return FileTypeModel.model_validate(orm, from_attributes=True)

    async def models_from_orm(self, orm: list[FileTypeOrmModel]) -> list[FileTypeModel]:
        return [await self.model_from_orm(item) for item in orm]


def create_file_type_repository(
    env: AuthUserEnvrimoment,
    database: AsyncSession,
) -> FileTypeRepository:
    return FileTypeRepositoryImpl(
        env=env,
        database=database,
    )


__all__ = [
    "FileTypeRepository",
    "create_file_type_repository",
]
