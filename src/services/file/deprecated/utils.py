import typing

from sqlalchemy.ext.asyncio import AsyncSession
from file import crud
from file.schemas import Tag


class MainTags:
    APPARATS: str = "Аппаратные"
    DISCIPLINES: str = "Дисциплины"
    LESSONS: str = "Занятия"
    KEYWORDS: str = "Ключевые слова"


TYPE_SEARCH = (
    {"name": "По названию", "value": "name"},
    {"name": "По ключевым словам", "value": "keywords"},
    {"name": "По описанию (векторный)", "value": "title_desc"},
    {"name": "Полнотекстовый поиск (векторный)", "value": "fulltext"},
)


class TypeContent:
    FRKP = "ФРКП"
    VIDEO_360 = "Видео 360"
    VIDEO = "Видео"
    MODEL_3D = "3D модель"
    TEST = "Тест"
    ELECTRONIC_BOOK = "Электронный учебник"
    ELECTRONIC_TABLE = "Электронные таблицы"
    PICTURE = "Картинка"
    PRESENTATION = "Презентация"
    LESSON_SCENARIO = "Сценарий занятия"
    TEXT_DOC = "Сценарий занятия"
    OTHERS = "Прочее"


def iter_file(
    path: str, size_chunk: int = 65536
) -> typing.Generator[bytes, None, None]:
    """
    Генератор для чтения файла частями (чанками) в бинарном режиме.
    Полезен для обработки больших файлов без загрузки в память целиком.

    :param path: Путь к файлу для чтения
    :param size_chunk: Размер одного чанка в байтах (по умолчанию 64KB)
    :return: Генератор, yield байтовые чанки файла

    """
    with open(path, mode="rb") as file:
        while chunk := file.read(size_chunk):
            yield chunk
