import enum
import pydantic


class UserBaseProviders(str, enum.Enum):
    """Перечень базовых поставщиков пользователей"""

    Local = "local"
    """Поставщик локальных учетных данных"""

    Trusted = "trusted"
    """Поставщик доверенных узлов"""

    EduSys = "edu_sys"
    """Поставщик системы обучения"""


class UserBasePermissions(str, enum.Enum):
    """Перечень базовых прав"""

    Admin = "admin"
    """Администратор"""

    Official = "official"
    """Офицер"""

    Metodis = "metodist"
    """Специалист методического отдела"""

    Teacher = "teacher"
    """Преподаватель"""

    Student = "student"
    """Обучающийся/Обучаемый"""


class UserSpecPermissions(str, enum.Enum):
    """Перечень специальных прав"""

    AuthSessions = "auth.sessions"
    """Просмотр сессий"""


class User(pydantic.BaseModel):
    """Базовая модель пользователя"""

    id: str = pydantic.Field(
        ...,
        description="идентифкатор",
    )
    provider: str = pydantic.Field(
        ...,
        description="поставщик",
    )
    username: str = pydantic.Field(
        ...,
        description="логин",
    )
    first_name: str = pydantic.Field(
        default="",
        description="имя",
    )
    last_name: str = pydantic.Field(
        default="",
        description="фамилия",
    )
    patronymic: str = pydantic.Field(
        default="",
        description="отчество",
    )
    permissions: list[str] = pydantic.Field(
        default_factory=list,
        description="права доступа",
    )

    @pydantic.computed_field
    def uuid(self) -> str:
        """Глобальный идентифкатор"""
        return f"{self.provider}.{self.id}"

    @pydantic.computed_field
    def full_name(self) -> str:
        """Полное имя пользователя ФИО"""
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    @pydantic.computed_field
    def short_name(self) -> str:
        """Короткое имя пользователя Ф И.О."""
        return f"{self.last_name} {self.first_name[:1]}. {self.patronymic[:1]}."

UserModel = User