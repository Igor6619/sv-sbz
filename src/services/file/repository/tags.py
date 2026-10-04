from uuid import UUID, uuid4
from abc import ABC, abstractmethod

from schemas import *
from utils.sbz.datastuctures import *
from utils.service import AuthUserEnvrimoment, UserModel
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import TagOrmModel


class FileTagRepository(ABC):
    """Репозиторий тегов фалов"""

    @abstractmethod
    async def get(self, id: UUID) -> TagOrmModel | None:
        """Получить тег"""

    @abstractmethod
    async def get_with_files(self, id: UUID) -> TagOrmModel | None:
        """Получить тег со связанными с ним файлами"""

    @abstractmethod
    async def get_by_code(self, code: str) -> TagOrmModel | None:
        """Получить тег по коду"""

    @abstractmethod
    async def get_by_name(self, name: str) -> TagOrmModel | None:
        """Получить тег по имени"""

    @abstractmethod
    async def values(self, filter: FileTagFilterSchema = None) -> list[TagOrmModel]:
        """Получить список тегов"""

    @abstractmethod
    async def create(self, schema: FileTagSchema) -> TagOrmModel:
        """Создать тег"""

    @abstractmethod
    async def move(self, schema: FileTagSchema) -> TagOrmModel:
        """Изменить родителя тега"""

    @abstractmethod
    async def update(self, schema: FileTagSchema) -> TagOrmModel:
        """Обновить тег"""

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить тег"""

    @abstractmethod
    async def keywords(
        self, values: list[str], create_if_not_exists: bool = True
    ) -> list[TagOrmModel]:
        """Получить список ключевых слов, при отсутсвии создается"""

    @abstractmethod
    async def model_from_orm(self, orm: TagOrmModel) -> FileTagModel:
        """Преобразовать в модель"""

    @abstractmethod
    async def model_from_orm_for_graph(self, orm: TagOrmModel) -> FileTagModel:
        """Преобразовать в модель"""

    @abstractmethod
    async def models_from_orm(self, orm: list[TagOrmModel]) -> list[FileTagModel]:
        """Преобразовать в модель"""


class FileTagRepositoryImpl(FileTagRepository):
    def __init__(
        self,
        env: AuthUserEnvrimoment,
        database: AsyncSession,
    ):
        super().__init__()
        self.env = env
        self.db = database

    async def get(self, id: UUID) -> TagOrmModel | None:
        tag = await self.db.get(
            TagOrmModel,
            id,
            options=[
                selectinload(TagOrmModel.children).subqueryload(TagOrmModel.children)
            ],
        )
        return tag

    async def get_with_files(self, id: UUID) -> TagOrmModel | None:
        tag = await self.db.get(
            TagOrmModel,
            id,
            options=[
                selectinload(TagOrmModel.files)
            ],
        )
        return tag

    async def get_by_code(self, code: str) -> TagOrmModel | None:
        tag = (
            (
                await self.db.execute(
                    select(TagOrmModel)
                    .where(TagOrmModel.enabled == True)
                    .where(TagOrmModel.code == code)
                    .options(
                        selectinload(TagOrmModel.children).subqueryload(
                            TagOrmModel.children
                        )
                    )
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )

        return tag

    async def get_by_name(self, name: str) -> TagOrmModel | None:
        tag = (
            (
                await self.db.execute(
                    select(TagOrmModel)
                    .where(TagOrmModel.enabled == True)
                    .where(TagOrmModel.name == name)
                    .options(
                        selectinload(TagOrmModel.children).subqueryload(
                            TagOrmModel.children
                        )
                    )
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )

        return tag

    async def values(self, filter: FileTagFilterSchema = None) -> list[TagOrmModel]:
        q = select(TagOrmModel).where(TagOrmModel.enabled == True)
        if filter is not None and filter.id is not None:
            q = q.where(TagOrmModel.id.in_(filter.id))

        if filter is not None and filter.name is not None:
            q = q.where(TagOrmModel.name.in_(filter.name))

        if filter is not None and filter.code is not None:
            q = q.where(TagOrmModel.code.in_(filter.code))

        if filter is not None and filter.exclude_code is not None:
            q = q.where(TagOrmModel.code.notin_(filter.exclude_code))

        if filter is not None and filter.keyword is not None:
            q = q.where(TagOrmModel.keyword == filter.keyword)

        if filter is not None and filter.parent is not None:
            q = q.where(TagOrmModel.parent_id.in_(filter.parent))

        exists = set[UUID]()
        result = list[TagOrmModel]()

        def insert_exists(tag: TagOrmModel):
            exists.add(tag.id)
            for child in tag.children:
                insert_exists(child)

        for tag in (
            (
                await self.db.execute(
                    q.options(
                        selectinload(TagOrmModel.children).subqueryload(
                            TagOrmModel.children
                        )
                    )
                )
            )
            .scalars()
            .all()
        ):
            if tag.id not in exists:
                insert_exists(tag)
                result.append(tag)

        return result

    async def create(self, schema: FileTagSchema) -> TagOrmModel:
        orm = (
            await self.db.get(TagOrmModel, schema.id) if schema.id is not None else None
        )
        if orm is not None:
            return await self.update(schema)

        if schema.name is None:
            raise ValueError(f"Имя тега не может быть пустым")

        orm = TagOrmModel(
            id=schema.id if schema.id is not None else uuid4(),
            name=schema.name if not schema.keyword else schema.name.lower(),
            code=schema.code,
            parent_id=schema.parent,
            enabled=True,
            keyword=schema.keyword,
        )
        self.db.add(orm)
        await self.db.commit()

        return await self.get(orm.id)

    async def move(self, schema: FileTagSchema) -> TagOrmModel:
        if schema.id is None:
            raise ValueError(f"Идентификатор тега не может быть пустым")

        if schema.parent is None:
            raise ValueError(f"Идентификатор родителя не может быть пустым")

        orm = await self.db.get(TagOrmModel, schema.id)
        if orm is None:
            raise ValueError(f"Тег с идентификатором {schema.id} не найден")

        orm.parent_id = schema.parent
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(orm)
        return orm

    async def update(self, schema: FileTagSchema) -> TagOrmModel:
        if schema.id is None:
            raise ValueError(f"Идентификатор тега не может быть пустым")

        orm = await self.db.get(TagOrmModel, schema.id)
        if orm is None:
            raise ValueError(f"Тег с идентификатором {schema.id} не найден")

        orm.name = schema.name
        orm.code = schema.code

        if schema.parent is not None:
            orm.parent_id = schema.parent

        orm.deleted = None

        await self.db.flush()
        await self.db.commit()
        return await self.get(orm.id)

    async def delete(self, id: UUID) -> None:
        if id is None:
            raise ValueError(f"Идентификатор тега не может быть пустым")

        orm = await self.db.get(TagOrmModel, id)
        if orm is None:
            raise ValueError(f"Тег с идентификатором {id} не найден")

        await self.db.delete(orm)
        await self.db.commit()

    async def keywords(
        self, values: list[str], create_if_not_exists: bool = True
    ) -> list[TagOrmModel]:
        names = list[str]()
        for value in values:
            names += [v.strip().lower() for v in value.split(",")]
        names = list(filter(lambda s: len(s) > 0, names))

        values = list(
            (
                await self.db.execute(
                    select(TagOrmModel)
                    .where(TagOrmModel.deleted == None)
                    .where(TagOrmModel.name.in_(values))
                    .options(
                        selectinload(TagOrmModel.children).subqueryload(
                            TagOrmModel.children
                        )
                    )
                )
            )
            .scalars()
            .all()
        )
        if create_if_not_exists:
            values_names = set([v.name for v in values])
            for name in names:
                if name not in values_names:
                    values.append(
                        await self.create(
                            FileTagSchema(
                                name=name,
                                keyword=True,
                            )
                        )
                    )

        return values

    async def model_from_orm(self, orm: TagOrmModel) -> FileTagModel:
        model = FileTagModel(
            id=orm.id,
            name=orm.name,
            code=orm.code,
            enabled=orm.enabled,
            keyword=orm.keyword,
            created=orm.created,
            modified=orm.modified,
            deleted=orm.deleted,
        )

        try:
            model.children = await self.models_from_orm(orm.children)
        except Exception as e:
            # import traceback
            # print(orm.id, orm.name, orm.children, e, traceback.format_exc())
            pass

        return model

    async def model_from_orm_for_graph(self, orm: TagOrmModel) -> TagModelForGraph:
        model = TagModelForGraph(
            id=str(orm.id),
            name=orm.name,
        )
        try:
            files = []
            for file in orm.files:
                file_model = FileModelForGraph(
                    id=str(file.id),
                    name=file.name,
                )
                files.append(file_model)
            model.children = files
        except Exception as e:
            import traceback
            print(orm.id, orm.name, orm.files, e, traceback.format_exc())
        return model

    async def models_from_orm(self, orm: list[TagOrmModel]) -> list[FileTagModel]:
        return [await self.model_from_orm(item) for item in orm]


def create_file_tag_repository(
    env: AuthUserEnvrimoment,
    database: AsyncSession,
) -> FileTagRepository:
    return FileTagRepositoryImpl(
        env=env,
        database=database,
    )


__all__ = [
    "FileTagRepository",
    "create_file_tag_repository",
]
