from uuid import UUID, uuid4
from pydantic import Field
from abc import ABC, abstractmethod
from utils.service import AuthUserEnvrimoment, UserModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models import UserOrmModel


class UserRepository(ABC):
    """Репозиторий пользователей"""

    @abstractmethod
    async def get(self, id: UUID) -> UserOrmModel | None:
        """Геттер пользователя"""

    @abstractmethod
    async def create(self, user: UserModel) -> UserOrmModel:
        """Создатель пользователя"""

    @abstractmethod
    async def get_all(self) -> list[UserOrmModel]:
        """Получить всех пользователей"""

    @abstractmethod
    async def update(self, user: UserModel) -> UserOrmModel:
        """Обновитель пользователя"""

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить пользователя"""

    @abstractmethod
    async def model_from_orm(self, orm: UserOrmModel) -> UserModel:
        """Преобразовать в модель"""

    @abstractmethod
    async def models_from_orm(self, orm: list[UserOrmModel]) -> list[UserModel]:
        """Преобразовать в модель"""


class UserRepositoryImpl(UserRepository):
    def __init__(
        self,
        env: AuthUserEnvrimoment,
        database: AsyncSession,
    ):
        super().__init__()
        self.env = env
        self.db = database

    async def get(self, id: UUID) -> UserOrmModel | None:
        return await self.db.get(UserOrmModel, id)

    async def create(self, user: UserModel) -> UserOrmModel:
        orm = (
            (
                await self.db.execute(
                    select(UserOrmModel)
                    .where(UserOrmModel.user_id == user.id)
                    .where(UserOrmModel.user_provider == user.provider)
                    .limit(1)
                )
            )
            .scalars()
            .first()
        )
        if orm is None:
            orm = UserOrmModel(
                id=uuid4(),
                user_id=user.id,
                username=user.username,
                user_provider=user.provider,
                first_name=user.first_name,
                last_name=user.last_name,
                patronymic=user.patronymic,
            )
            self.db.add(orm)
            await self.db.flush()
            await self.db.commit()

        return orm

    async def get_all(self) -> list[UserOrmModel]:
        return list((await self.db.execute(select(UserOrmModel))).scalars().all())

    async def update(self, user: UserModel) -> UserOrmModel:
        await self.db.execute(
            update(UserOrmModel)
            .where(UserOrmModel.user_id == user.id)
            .where(UserOrmModel.user_provider == user.provider)
            .values(
                last_name=user.last_name,
                first_name=user.first_name,
                patronymic=user.patronymic,
            )
        )
        await self.db.flush()
        await self.db.commit()
        return await self.get(user)

    async def delete(self, id: UUID) -> None:
        raise NotImplementedError(f"Метод удаления пользователей не реализован")

    async def model_from_orm(self, orm: UserOrmModel) -> UserModel:
        return UserModel(
            id=orm.user_id,
            provider=orm.user_provider,
            first_name=orm.first_name,
            last_name=orm.last_name,
            patronymic=orm.patronymic,
        )

    async def models_from_orm(self, orm: list[UserOrmModel]) -> list[UserModel]:
        return [await self.model_from_orm(item) for item in orm]


def create_user_repository(
    env: AuthUserEnvrimoment,
    database: AsyncSession,
) -> UserRepository:
    return UserRepositoryImpl(env, database)


__all__ = ["UserRepository", "create_user_repository"]
