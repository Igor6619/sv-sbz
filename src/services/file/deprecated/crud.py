import logging
import typing
from uuid import UUID

from pydantic.v1 import UUID4
from sqlalchemy import select, delete, update, and_, alias, inspect, or_, func
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .log import logger
from .models import FileOrmModel, FileTypeOrmModel  # , TagTree
from .schemas import (
    FileCreate as FileCreateSch,
    FileType as FileTypeSch,
    FileUpdate as FileUpdateSch,
)
from sqlalchemy.orm import selectinload


T = typing.TypeVar("T")


async def get_all_model(db: AsyncSession, model: T) -> typing.List[T]:
    """
    Асинхронно извлекает все записи указанной модели из базы данных.

    :param db: Экземпляр AsyncSession для работы с базой данных.
    :param model: Класс модели SQLAlchemy, данные которой нужно получить.
    :return: Список объектов модели.
    :raises SQLAlchemyError: Если произошла ошибка при работе с базой данных.
    """
    try:
        # Создаем запрос на выборку всех записей модели
        stmt = select(model)
        result = await db.execute(stmt)
        # Извлекаем скалярные значения (объекты модели)
        result: List[T] = result.scalars().all()
        return result
    except SQLAlchemyError as e:
        # Логируем ошибку и пробрасываем исключение выше
        logger.log(logging.ERROR, f"Database error: {e}")


async def get_list_by_pks(
    db: AsyncSession, model: T, pks: typing.List
) -> typing.List[T]:
    """
    Асинхронно получает записи из указанной таблицы по списку первичных ключей (pks).

    :param db: Асинхронная сессия SQLAlchemy.
    :param pks: Список первичных ключей (id).
    :param model: Модель для запроса.
    :return: Список объектов File.
    """
    if not pks:
        return []

    # Получение первичного ключа
    inspector = inspect(model)
    primary_key = inspector.primary_key[0]

    # Выборка записей по первичным ключам
    stmt = select(model).where(primary_key.in_(pks))
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_files_by_filters(
    db: AsyncSession,
    filter_search_type,
    name: str,
    file_type_pk: UUID,
    tags_pk: typing.List,
) -> typing.List[FileOrmModel]:
    stmt = select(FileOrmModel)
    filters = []

    if name:
        match filter_search_type:
            case "name":
                filters.append(func.lower(FileOrmModel.name).contains(name.lower().strip()))
            case "keywords":
                keywords_srt: List[str] = [
                    keyword.lower().strip() for keyword in name.split() if keyword
                ]
                conditions = [
                    func.lower(TagOrmModel.name).contains(keyword.lower())
                    for keyword in keywords_srt
                    if keyword
                ]
                # TODO Срабатывает только последнее условие, предположительно идет перезапись условия.
                # TODO Необходимо исправит!
                keywords_idx = await db.execute(select(TagOrmModel.id).where(or_(*conditions)))
                keywords = keywords_idx.scalars().all()

                if keywords:
                    tags_pk += keywords
                else:
                    tags_pk = []
            case "title_desc":
                ...
            case "fulltext":
                ...

    if file_type_pk:
        filters.append(FileOrmModel.file_type_pk == file_type_pk)
    if filters:
        stmt = stmt.where(and_(*filters))

    if tags_pk and name:  # Если tags_pk = [], то условие не добавится
        stmt = stmt.join(FileOrmModel.tags).where(TagOrmModel.id.in_(tags_pk))

    result = await db.execute(stmt)

    return list(set(result.scalars().all()))


async def create_file_type(
    file_type_list: list[FileTypeSch], session: AsyncSession
) -> Optional[list[FileTypeOrmModel]]:
    result = []
    session = session
    for file_type_sch in file_type_list:
        file_type = (
            await session.execute(
                select(FileTypeOrmModel).filter(FileTypeOrmModel.name == file_type_sch.name)
            )
        ).scalar_one_or_none()

        if not file_type:
            file_type = FileTypeOrmModel(name=file_type_sch.name)
            session.add(file_type)
            await session.commit()
            await session.refresh(file_type)

        result.append(file_type)
    return result


async def get_file(db: AsyncSession, file_id: UUID):
    stmt = select(FileOrmModel).options(selectinload(FileOrmModel.tags)).filter(FileOrmModel.id == file_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_files(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(FileOrmModel).options(selectinload(FileOrmModel.tags)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_file(db: AsyncSession, file: FileCreateSch, user: int):
    db_file = FileOrmModel(
        name=file.name,
        path=f"uploads/{file.name}",  # временно
        owner_pk=user,
        file_type_pk=file.file_type_pk,
    )
    db.add(db_file)
    if file.tags:
        db_file.tags = [await get_tag(db, tag_uuid) for tag_uuid in file.tags]
    await db.commit()
    await db.refresh(db_file)
    return db_file


async def update_file(db: AsyncSession, file_uuid: UUID, file_update: FileUpdateSch):
    stmt = (
        update(FileOrmModel)
        .where(FileOrmModel.uuid == file_uuid)
        .values(**file_update.dict(exclude_unset=True))
    )
    await db.execute(stmt)
    await db.commit()
    return await get_file(db, file_uuid)


async def delete_file(db: AsyncSession, file_id: UUID):
    stmt = delete(FileOrmModel).where(FileOrmModel.id == file_id)
    await db.execute(stmt)
    await db.commit()


################## START TAG ##############

from fastapi import HTTPException
from .models import TagOrmModel, FileOrmModel
from . import schemas as sch
from typing import List


async def create_tag(db: AsyncSession, tag: sch.TagCreate) -> TagOrmModel:
    new_tag: TagOrmModel = TagOrmModel(**tag.dict())
    if tag.parent_id:
        parent = await db.get(TagOrmModel, tag.parent_id)
        if not parent:
            raise HTTPException(404, "Родительский тег не найден")
        new_tag.parent = parent

    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)

    return new_tag


async def get_tag_by_name(db: AsyncSession, tag_name: str) -> typing.Optional[TagOrmModel]:
    tag = (await db.execute(select(TagOrmModel).where(TagOrmModel.name == tag_name))).scalars().first()
    return tag


async def get_tag(db: AsyncSession, tag_id: UUID4) -> TagOrmModel:
    tag = await db.get(TagOrmModel, tag_id, options=[selectinload(TagOrmModel.children)])
    if not tag:
        raise HTTPException(404, "Тег не найден")
    return tag


async def get_tags(db: AsyncSession) -> List[TagOrmModel]:
    result = await db.execute(select(TagOrmModel).options(selectinload(TagOrmModel.children)))
    return result.scalars().all()


async def update_tag(db: AsyncSession, tag_id: UUID4, tag_update: sch.TagUpdate) -> TagOrmModel:
    tag = await get_tag(db, tag_id)

    if tag_update.name:
        tag.name = tag_update.name

    if tag_update.parent_id:
        parent = await db.get(TagOrmModel, tag_update.parent_id)
        if not parent:
            raise HTTPException(404, "Новый родительский тег не найден")
        tag.parent = parent

    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, tag_id: UUID4) -> dict:
    tag = await get_tag(db, tag_id)
    await db.delete(tag)
    await db.commit()
    return {"detail": "Тег удален"}


async def create_tags_from_file(db: AsyncSession, tag: dict) -> dict:

    new_tag = await create_tag(
        db, sch.TagCreate(name=tag["name"], parent_id=tag.get("parent_id", None))
    )
    if "children" in tag and len(tag["children"]):
        for tag_child in tag["children"]:
            tag_child["parent_id"] = new_tag.id
            await create_tags_from_file(db, tag_child)

    return {"detail": "Теги добавлены"}


async def get_all_descendants(db: AsyncSession, tag_id: UUID):
    # Создаем псевдоним для таблицы tags
    tags_alias = alias(TagOrmModel)

    # Рекурсивный CTE (Common Table Expression)
    recursive_cte = (
        select(TagOrmModel)
        .where(TagOrmModel.id == tag_id)  # Начинаем с текущего тега
        .cte(recursive=True)
    )

    # Добавляем рекурсивную часть
    recursive_cte = recursive_cte.union(
        select(TagOrmModel).join(tags_alias, TagOrmModel.parent_id == tags_alias.c.id)
    )

    result = await db.execute(
        select(TagOrmModel).join(recursive_cte, TagOrmModel.id == recursive_cte.c.id)
    )
    return result.scalars().all()


################## END TAGTREE ##############
