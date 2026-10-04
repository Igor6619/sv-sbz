import os

from core.config import settings
from pathlib import Path
from datetime import date
import mimetypes


def get_media_type(filename: str) -> str:
    media_type, _ = mimetypes.guess_type(filename)
    return media_type or "application/octet-stream"


def get_storage_files_dir() -> str:
    base_dir = Path(settings.storage_files_dir).resolve()
    return str(base_dir)


def get_path_for_file_save(file_name: str) -> str:
    today = date.today()
    base_dir = Path(get_storage_files_dir())
    folder_dir = base_dir.joinpath(today.strftime("%Y"), today.strftime("%d.%m"))
    folder_dir.mkdir(parents=True, exist_ok=True)

    name, ext = os.path.splitext(file_name)
    counter = 1  # Счетчик для уникального суффикса

    # Формируем начальный путь
    file_path = folder_dir.joinpath(file_name)

    while file_path.exists():
        # Если файл существует, добавляем суффикс к имени
        new_name = f"{name}-({counter}){ext}"
        file_path = folder_dir.joinpath(new_name)
        counter += 1

    return str(file_path)
