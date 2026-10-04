import uuid as uuid_pkg
from enum import Enum
from datetime import datetime
from typing import Optional

from sqlalchemy import func, Table, ForeignKey, Column, BigInteger, Enum as SAEnum
from sqlalchemy import (
    JSON,
    String,
    Text,
    Integer,
    DateTime,
    Boolean,
    false,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from schemas import FileSearchType


# БАЗОВЫЕ МОДЕЛИ БАЗЫДАННЫХ
class ExtraInfoMixin:
    """Mixin дополнительных меток времени"""

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        index=True,
        server_default=func.now(),
        comment="Время создания",
    )
    deleted: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        index=True,
        default=None,
        comment="Время удаления",
    )
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        index=True,
        server_default=func.now(),
        comment="Время последнего изменения",
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, comment="")


class BaseOrmModel(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid_pkg.uuid4,
    )


class BaseMaxOrmModel(BaseOrmModel, ExtraInfoMixin):
    __abstract__ = True


# ПОЛЬЗОВАТЕЛИ
class UserOrmModel(BaseOrmModel):
    """
    Модель описывает пользователей.
    """

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(128),
        comment="Идентификатор пользователя",
    )

    user_provider: Mapped[str] = mapped_column(
        String(128),
        index=True,
        comment="Поставщик учетных данных",
    )

    username: Mapped[str] = mapped_column(
        String(128),
        index=True,
        comment="Логин пользователя",
    )

    first_name: Mapped[str] = mapped_column(
        String(128),
        comment="Имя пользователя",
    )

    last_name: Mapped[str] = mapped_column(
        String(128),
        comment="Фамилия пользователя",
    )

    patronymic: Mapped[str] = mapped_column(
        String(128),
        comment="Отчество пользователя",
    )

    files: Mapped[list["FileOrmModel"]] = relationship(
        "FileOrmModel",
        back_populates="owner",
    )

    # edit_files: Mapped[list["FileOrmModel"]] = relationship(
    #     "FileOrmModel",
    #     back_populates="edit_files",
    # )

    file_access_logs: Mapped["FileAccessLogOrmModel"] = relationship(
        "FileAccessLogOrmModel",
        back_populates="user",
    )

    filters: Mapped[list["UserFilterOrmModel"]] = relationship(
        "UserFilterOrmModel",
        back_populates="owner",
    )

    def __str__(self):
        return str(self.id)


# Association table for many-to-many relationship between files and tags
file_tag_association = Table(
    "file_tag_association",
    BaseMaxOrmModel.metadata,
    Column("file_id", UUID(as_uuid=True), ForeignKey("files.id")),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id")),
)


class TagOrmModel(BaseMaxOrmModel):
    """Представление тега/ключевого слова"""

    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(
        String,
        index=True,
        nullable=False,
        comment="Название тега",
    )

    code: Mapped[str | None] = mapped_column(
        String,
        index=True,
        nullable=True,
        comment="Уникальный код тега",
    )

    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tags.id"),
        nullable=True,
        comment="Родительский тег",
    )

    # Связь с родительским тегом (один к одному)
    parent: Mapped["TagOrmModel"] = relationship(
        "TagOrmModel",
        remote_side="TagOrmModel.id",  # Указывает, что это самоссылка
        back_populates="children",
        lazy="selectin",
    )

    # Связь с дочерними тегами (один ко многим)
    children: Mapped[list["TagOrmModel"]] = relationship(
        "TagOrmModel",
        back_populates="parent",
        lazy="subquery",
        order_by="TagOrmModel.name"
    )

    keyword: Mapped[Boolean] = mapped_column(
        Boolean,
        index=True,
        comment="Принадлежность к ключевому слову",
    )

    filters_of_discipline: Mapped[list["UserFilterOrmModel"]] = relationship(
        "UserFilterOrmModel",
        back_populates="discipline",
        foreign_keys="[UserFilterOrmModel.discipline_id]"
    )
    filters_of_equipment: Mapped[list["UserFilterOrmModel"]] = relationship(
        "UserFilterOrmModel",
        back_populates="equipment",
        foreign_keys="[UserFilterOrmModel.equipment_id]"
    )

    def __repr__(self):
        return f"<Tag(name='{self.name}', id='{self.id}')>"

    files: Mapped[list["FileOrmModel"]] = relationship(
        "FileOrmModel",
        secondary=file_tag_association,
        back_populates="tags",
    )


class FileTypeCode(str, Enum):
    FRKP = "frkp"
    VIDEO_360 = "video_360"


class FileTypeOrmModel(BaseMaxOrmModel):
    __tablename__ = "file_types"

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Название типа файла",
    )

    code: Mapped[str | None] = mapped_column(
        String,
        index=True,
        nullable=True,
        comment="Уникальный код",
    )

    extensions: Mapped[list[str]] = mapped_column(
        JSON(none_as_null=False), default=list[str](), server_default="'[]'"
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean, index=True, default=False, server_default=false()
    )

    files: Mapped[list["FileOrmModel"]] = relationship(
        "FileOrmModel",
        back_populates="type",
    )

    filters: Mapped[list["UserFilterOrmModel"]] = relationship(
        "UserFilterOrmModel",
        back_populates="file_type",
    )


class FileOrmModel(BaseMaxOrmModel):
    """
    Модель для описания файла
    """

    __tablename__ = "files"

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Название файла",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Описание файла",
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Публичный файл",
    )

    # Внешний ключ для пользователя
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["UserOrmModel"] = relationship(
        "UserOrmModel", back_populates="files", lazy="selectin"
    )

    # Внешний ключ для пользователя который последний обновил сонтент файла
    # last_edit_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    # last_edit_user: Mapped["UserOrmModel"] = relationship(
    #     "UserOrmModel",
    #     back_populates="edit_files",
    # )

    tags: Mapped[list["TagOrmModel"]] = relationship(
        "TagOrmModel",
        secondary=file_tag_association,
        back_populates="files",
        lazy="selectin",
    )

    # Внешний ключ для типа файла
    type_id: Mapped[UUID] = mapped_column(ForeignKey("file_types.id"))
    type: Mapped["FileTypeOrmModel"] = relationship(
        "FileTypeOrmModel", back_populates="files", lazy="selectin"
    )

    # Внешний ключ для контента файла
    content_id: Mapped[UUID] = mapped_column(ForeignKey("file_contents.id"))
    content: Mapped["FileContentOrmModel"] = relationship(
        "FileContentOrmModel", back_populates="files", lazy="selectin"
    )


class FileContentOrmModel(BaseMaxOrmModel):
    """
    Модель хранилища файлов
    """

    __tablename__ = "file_contents"

    path: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Путь к файлу",
    )

    size: Mapped[int] = mapped_column(
        BigInteger,
        comment="Размер файла",
    )

    mimetype: Mapped[str] = mapped_column(
        String(100),
        index=True,
        comment="Mimetype файла",
    )

    extension: Mapped[str] = mapped_column(
        String(20),
        index=True,
        comment="Расширение файла",
    )

    # Контрольные суммы для проверки целостности
    md5_checksum: Mapped[str] = mapped_column(
        String(32),
        nullable=True,
        comment="MD5 контрольная сумма",
    )
    sha256_checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=True,
        comment="SHA256 контрольная сумма",
    )

    # Связь с файлами (один контент ко многим файлам)
    files: Mapped[list["FileOrmModel"]] = relationship(
        "FileOrmModel",
        back_populates="content",
    )

    # Связь с логами доступа
    access_logs: Mapped[list["FileAccessLogOrmModel"]] = relationship(
        "FileAccessLogOrmModel",
        back_populates="file_content",
    )


class FileAccessLogOrmModel(BaseMaxOrmModel):
    """
    Модель для отслеживания обращений к файлам пользователями.
    Если к файлу обращался гость, то поле user_id будет None.
    """

    __tablename__ = "file_access_logs"

    # Внешний ключ для контента файла
    file_content_id: Mapped[UUID] = mapped_column(ForeignKey("file_contents.id"))
    file_content: Mapped[FileContentOrmModel] = relationship(
        "FileContentOrmModel",
        back_populates="access_logs",
    )

    # Внешний ключ для пользователя (может быть None для гостей)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[UserOrmModel] = relationship(
        "UserOrmModel",
        back_populates="file_access_logs",
    )

    # IP адрес пользователя (опционально для отслеживания)
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # Достаточно для IPv6
        nullable=True,
        comment="IP адрес пользователя",
    )

    # User agent (опционально для отслеживания)
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User agent браузера",
    )


class SearchQueryOrmModel(BaseMaxOrmModel):
    """
    Модель хранилища поисковых запросов
    """
    __tablename__ = "search_queries"

    value: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Строка запроса",
    )
    results_count: Mapped[int] = mapped_column(
        Integer,
        comment="Количество найденных материалов по запросу",
    )


class UserFilterOrmModel(BaseMaxOrmModel):
    """
    Модель хранилища пользовательских фильтров
    """
    __tablename__ = "user_filters"

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Название пользовательского фильтра",
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Публичный фильтр",
    )

    # Внешний ключ для пользователя
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["UserOrmModel"] = relationship(
        "UserOrmModel",
        back_populates="filters",
        lazy="selectin",
    )

    search_type: Mapped[FileSearchType] = mapped_column(
        SAEnum(
            FileSearchType,
            native_enum=False,
            length=50,
            create_constraint=True,
        ),
        default=FileSearchType.Name.value,
        comment="Тип поиска"
    )

    # Внешний ключ для типа файла
    file_type_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("file_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    file_type: Mapped[Optional["FileTypeOrmModel"]] = relationship(
        "FileTypeOrmModel",
        back_populates="filters",
        lazy="selectin",
    )

    # Внешний ключ для дисциплины
    discipline_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("tags.id", ondelete="SET NULL"),
        nullable=True,
    )
    discipline: Mapped[Optional["TagOrmModel"]] = relationship(
        "TagOrmModel",
        back_populates="filters_of_discipline",
        foreign_keys=[discipline_id],
        lazy="selectin",
    )

    # Внешний ключ для аппаратной
    equipment_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("tags.id", ondelete="SET NULL"),
        nullable=True,
    )
    equipment: Mapped[Optional["TagOrmModel"]] = relationship(
        "TagOrmModel",
        back_populates="filters_of_equipment",
        foreign_keys=[equipment_id],
        lazy="selectin",
    )


__all__ = [
    "ExtraInfoMixin",
    "BaseOrmModel",
    "BaseMaxOrmModel",
    "UserOrmModel",
    "TagOrmModel",
    "FileTypeCode",
    "FileTypeOrmModel",
    "FileOrmModel",
    "FileContentOrmModel",
    "FileAccessLogOrmModel",
    "SearchQueryOrmModel",
    "UserFilterOrmModel",
]
