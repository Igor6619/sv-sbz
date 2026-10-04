from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Импортируй свои ORM модели и репозиторий
from services.file.repository.files import FileRepositoryImpl
from models import TagOrmModel, FileOrmModel 

def str_clipped(text: str) -> str:
    """Вспомогательная функция для обрезки текста"""
    if text is None:
        return "Без названия"
    text_str = text if isinstance(text, str) else str(text)
    return (text_str[:97] + "...") if len(text_str) > 100 else text_str


async def get_file_graph(repository: FileRepositoryImpl, file_id: str) -> dict:
    """Собирает данные: Корень (Файл) -> Дети (Теги)"""
    file_uuid = UUID(file_id) if isinstance(file_id, str) else file_id
    
    # Используем штатный метод репозитория, который подгружает все связи
    file_item = await repository.get(file_uuid)
    
    if not file_item:
        return {"id": str(file_id), "type": "file", "name": "Файл не найден", "children": []}

    children_tags = [
        {
            "id": str(tag.id), 
            "type": "tag",
            "keyword": tag.keyword, 
            "name": str_clipped(getattr(tag, "name", "Без названия"))
        } 
        for tag in file_item.tags
    ]

    return {
        "id": str(file_item.id),
        "type": "file",
        "name": str_clipped(getattr(file_item, "name", "Без названия")),
        "children": children_tags
    }


async def get_tag_graph(repository: FileRepositoryImpl, tag_id: str) -> dict:
    """Собирает данные: Корень (Тег) -> Дети (Файлы)"""
    tag_uuid = UUID(tag_id) if isinstance(tag_id, str) else tag_id
    
    # Так как в репозитории нет get для тегов, лезем в сессию напрямую через repository.db
    query = (
        select(TagOrmModel)
        .where(TagOrmModel.id == tag_uuid)
        .options(selectinload(TagOrmModel.files))  # Замени "files" на имя связи в TagOrmModel
    )
    result = await repository.db.execute(query)
    tag = result.scalar_one_or_none()
    
    if not tag:
        return {"id": str(tag_id), "type": "tag", "name": "Тег не найден", "children": []}
        
    children_files = [
        {
            "id": str(file_item.id),
            "type": "file",
            "name": str_clipped(getattr(file_item, "name", "Без названия"))
        }
        for file_item in getattr(tag, "files", [])
    ]

    return {
        "id": str(tag.id),
        "type": "tag",
        "keyword": tag.keyword,
        "name": str_clipped(getattr(tag, "name", "Без названия")),
        "children": children_files
    }