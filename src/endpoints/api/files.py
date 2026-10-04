import os
import uuid
import fastapi
import tempfile
import asyncio
import shutil
import aiofiles
from typing import Optional

from fastapi.templating import Jinja2Templates
from depends import *
from models import FileTypeCode
from services import FileRepository
from utils.sbz.datastuctures.models import FileModel
from utils.sbz.datastuctures.schemas import FileSchema, FileFilterSchema
from utils.service import AuthUserEnvrimoment
from utils.service.depends import AuthEnvrimomentOrNone
from pathlib import Path
import aiofiles.os

api_files_router = fastapi.routing.APIRouter()
templates = Jinja2Templates(
    directory=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    )
)


def is_360(file: FileModel) -> bool:
    return file.type.code in [FileTypeCode.FRKP.value, FileTypeCode.VIDEO_360.value]


templates.env.filters["is_360"] = is_360

@api_files_router.get("/{id}/download")
async def api_download_file(
    id: str,
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired),
):
    """Скачать файл по идентификатору"""
    file = await repository.get(uuid.UUID(id))
    path = await repository.get_path(uuid.UUID(id))
    # if file is None or path is None or not os.path.exists(path):
    #     raise fastapi.HTTPException(status_code=404, detail="File not found")

    if file is None:
        raise fastapi.HTTPException(status_code=404, detail="Файл не найден в базе данных (DB)")
    if path is None:
        raise fastapi.HTTPException(status_code=404, detail="Репозиторий не вернул путь к файлу")
    if not os.path.exists(path):
        raise fastapi.HTTPException(status_code=404, detail=f"Файл отсутствует на диске по пути: {path}")
    is_biblio = file.content.extension == '.bdt'
    filename = str(file.id) + file.content.extension if is_biblio else file.name + file.content.extension
    return fastapi.responses.FileResponse(
        path,
        filename=filename,
        media_type=file.content.mimetype,
    )


@api_files_router.get("/{id}")
async def api_get_file(
    id: str,
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired),
) -> FileModel | None:
    """Получить файл по идентификатору"""
    r = await repository.get(uuid.UUID(id))
    return await repository.model_from_orm(r) if r is not None else None




@api_files_router.get("/{id}/preview")
async def api_file_preview(
    id: str,
    request: fastapi.Request,
    env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired),
):
    file = await repository.get(uuid.UUID(id))
    path = await repository.get_path(uuid.UUID(id))
    # if file is None or path is None or not os.path.exists(path):
    #     raise fastapi.HTTPException(status_code=404, detail="File not found")
    if file is None:
        raise fastapi.HTTPException(status_code=404, detail="ПРЕВЬЮ: Файл не найден в базе данных (DB)")
    if path is None:
        raise fastapi.HTTPException(status_code=404, detail="ПРЕВЬЮ: Репозиторий не вернул путь к файлу")
    if not os.path.exists(path):
        raise fastapi.HTTPException(status_code=404, detail=f"ПРЕВЬЮ: Файл отсутствует на диске по пути: {path}")

   

    context = {
        "request": request,
        "user": env.user if env is not None else None,
        "file": file,
        
    }

    return templates.TemplateResponse("files/preview.html", context=context)




from starlette.background import BackgroundTasks 
 # 0. Выносим очистку в отдельную изолированную функцию
def cleanup_libreoffice_env(unique_home: str, profile_path: str):
    """Синхронная функция очистки, которая будет выполняться в фоне"""
    if os.path.exists(unique_home):
        shutil.rmtree(unique_home, ignore_errors=True)
    if os.path.exists(profile_path):
        shutil.rmtree(profile_path, ignore_errors=True)

# Создаем общую папку для кэша внутри контейнера
PDF_OUTPUT_DIR = Path("/var/sbz/pdf_output")
PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@api_files_router.get("/{id}/pdf")
async def api_file_pdf_stream(
    id: str,
    background_tasks: BackgroundTasks, 
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired)
):
    '''
    Конвертация office в pdf 
    '''

   

    # 1. Валидация UUID
    try:
        file_uuid = uuid.UUID(id)
    except ValueError:
        raise fastapi.HTTPException(status_code=400, detail="Некорректный формат UUID")

    # 2. Проверка наличия записи в БД
    file = await repository.get(file_uuid)
    if file is None:
        raise fastapi.HTTPException(status_code=404, detail="КОНВЕРТАЦИЯ: Файл не найден в БД")

    # 3. Проверка пути и физического наличия исходного файла
    path_str = await repository.get_path(file_uuid)
    if path_str is None or not await aiofiles.os.path.exists(path_str):
        raise fastapi.HTTPException(status_code=404, detail="КОНВЕРТАЦИЯ: Исходный файл отсутствует")

    # 4 если оригинал файла имеет расширение pdf то его сразу отправляем в браузер
    if Path(path_str).suffix.lower()=='.pdf':
       return fastapi.responses.FileResponse(
               path_str,
               media_type="application/pdf",
               headers={"Content-Disposition": "inline"}
           ) 

    # 5. Если готовый кэш по ID уже существует — отдаем его 
    output_pdf_path = PDF_OUTPUT_DIR / f"{id}.pdf"
    if await aiofiles.os.path.exists(output_pdf_path):
        return fastapi.responses.FileResponse(
            output_pdf_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )

    # 6. Подготовка уникального изолированного окружения
    unique_profile = f"/tmp/libreoffice_profile_{id}"
    unique_home = f"/tmp/libreoffice_home_{id}"

    # КРИТИЧЕСКИЙ ФИКС: Обязательно создаем физическую папку для HOME на диске
    os.makedirs(unique_home, exist_ok=True)

    cmd = [
        "xvfb-run",
        "--auto-servernum",
        "libreoffice",
        f"-env:UserInstallation=file://{unique_profile}",
        "--headless",
        "--convert-to", "pdf:calc_pdf_Export:{\"SinglePageSheets\":{\"type\":\"boolean\",\"value\":\"true\"}}",
        "--outdir", str(PDF_OUTPUT_DIR),
        path_str
    ]

    env = os.environ.copy()
    env["XDG_RUNTIME_DIR"] = unique_home
    env["HOME"] = unique_home
    env["SAL_USE_VCLPLUGIN"] = "gen"

    # cmd = [
        
    #     "libreoffice",
    #     f"-env:UserInstallation={unique_profile}",
    #     "--headless",
    #     '--infilter=Calc_PDF_Export:{"SinglePageSheets":{"type":"boolean","value":"true"}}',
    #     "--convert-to", "pdf",
    #     "--outdir", str(PDF_OUTPUT_DIR),
    #     path_str
    # ]
    try:
        # 7. Запуск процесса конвертации
        process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                )
        stdout, stderr = await process.communicate()

        # Если LibreOffice упал — выводим лог ошибки
        if process.returncode != 0:
            error_log = stderr.decode(errors='ignore') or stdout.decode(errors='ignore')
            print(f"КРИТИЧЕСКАЯ ОШИБКА LIBREOFFICE: {error_log}")
            cleanup_libreoffice_env(unique_home, unique_profile)
            raise fastapi.HTTPException(
                status_code=500,
                detail=f"Ошибка конвертации (код {process.returncode}): {error_log[:100]}"
            )
        # if process.returncode != 0:
        #     print(f"Ошибка LibreOffice CLI: {stderr.decode()}")
        #     raise fastapi.HTTPException(status_code=500, detail=f"Ошибка при конвертации документа in PDF: {stderr.decode()[:100]}")
        # 8. Поиск созданного файла и переименование в ID.pdf
        expected_original_name_pdf = PDF_OUTPUT_DIR / (Path(path_str).stem + ".pdf")
        
        if await aiofiles.os.path.exists(expected_original_name_pdf):
            if expected_original_name_pdf != output_pdf_path:
                # Защита от конфликта имен при перезаписи кэша
                if await aiofiles.os.path.exists(output_pdf_path):
                    await aiofiles.os.remove(output_pdf_path)
                await aiofiles.os.rename(expected_original_name_pdf, output_pdf_path)
        else:
            # Если папка пуста — выводим дебаг в консоль
            print("ОШИБКА: Файл не найден. LO STDOUT:", stdout.decode(errors='ignore'))
            print("ОШИБКА: Файл не найден. LO STDERR:", stderr.decode(errors='ignore'))
            cleanup_libreoffice_env(unique_home, unique_profile)
            raise fastapi.HTTPException(status_code=500, detail="Ошибка сохранения PDF-файла в кэш")

    except Exception:
        # Если упало любое непредвиденное исключение во время конвертации — чистим диск
        cleanup_libreoffice_env(unique_home, unique_profile)
        raise

    background_tasks.add_task(cleanup_libreoffice_env, unique_home, unique_profile)    
        
    # finally:
    #     # 9. Очистка временного мусора после завершения (успешного или с ошибкой)
    #     # Удаляем созданный unique_home (включая профиль внутри /tmp если LibreOffice наследовал пути)
    #     if os.path.exists(unique_home):
    #         shutil.rmtree(unique_home, ignore_errors=True)

    #     # Так как профиль LibreOffice создается как папка, чистим и её текстовый путь в /tmp
    #     profile_raw_path = f"/tmp/libreoffice_profile_{id}"
    #     if os.path.exists(profile_raw_path):
    #         shutil.rmtree(profile_raw_path, ignore_errors=True)

    # 10. Возвращаем готовый файл из кэша в браузер
    return fastapi.responses.FileResponse(
        output_pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"}
    )
       



# # генерирует конфигурационный JSON для инициализации редактора ONLYOFFICE на фронтенде.
# SBZ_SERVER_IP = "172.31.21.251"  # Замените на реальный IP вашего сервера в локальной сети

# # Карта соответствия расширений типам редакторов ONLYOFFICE
# DOCUMENT_TYPES = {
#     # Текстовые документы (Word) -> 'word'
#     'docx': 'word', 'doc': 'word', 'odt': 'word', 'rtf': 'word', 'txt': 'word',
#     # Таблицы (Excel) -> СТРОГО 'cell'
#     'xlsx': 'cell', 'xls': 'cell', 'ods': 'cell', 'csv': 'cell',
#     # Презентации (PowerPoint) -> СТРОГО 'slide'
#     'pptx': 'slide', 'ppt': 'slide', 'odp': 'slide'
   
# }

# @api_files_router.get("/{file_id}/onlyoffice-config")
# async def get_onlyoffice_config(
#         file_id: str, 
#         repository: FileRepository = fastapi.Depends(FileRepositoryRequired)
#     ):
#     """
#     Эндпоинт генерирует конфигурационный JSON для инициализации редактора ONLYOFFICE на фронтенде.
#     """
    
#     # -------------------------------------------------------------------------
#     # ШАГ 1: Получение данных о файле из вашей базы данных или файловой системы
#     # -------------------------------------------------------------------------
#     # Имитируем получение данных. Вам нужно заменить это на вашу реальную логику:
#     # file_obj = await db.get_file(file_id)
#     try:
#         file_uuid = uuid.UUID(file_id)
#     except ValueError:
#         raise fastapi.HTTPException(status_code=400, detail="Некорректный формат UUID")

#     file = await repository.get(file_uuid)
#     path_str = await repository.get_path(file_uuid)

#     filename = file.name
#     file_ext = Path(path_str).suffix.lower().strip().lstrip('.')

#     # Проверяем, поддерживает ли ONLYOFFICE такой формат
#     if file_ext not in DOCUMENT_TYPES:
#         raise fastapi.HTTPException(
#             status_code=400, 
#             detail=f"Формат файла .{file_ext} не поддерживается редактором ONLYOFFICE"
#         )

#     # -------------------------------------------------------------------------
#     # ШАГ 2: Формирование внутренних URL-адресов для Docker-контейнера
#     # -------------------------------------------------------------------------
#     # URL, по которому ONLYOFFICE скачает файл в память для редактирования
#     # document_url = f"http://{SBZ_SERVER_IP}:8075/api/files/{file_id}/download"
#     document_url = f"http://host.docker.internal:8075/api/files/{file_id}/download"
#     # URL, на который ONLYOFFICE пришлет POST-запрос с готовым файлом при сохранении
#     # callback_url = f"http://{SBZ_SERVER_IP}:8075/api/files/{file_id}/onlyoffice-callback"
#     callback_url = f"http://host.docker.internal:8075/api/files/{file_id}/onlyoffice-callback"
#     # -------------------------------------------------------------------------
#     # ШАГ 3: Возврат конфигурации в формате, который требует DocsAPI.DocEditor
#     # -------------------------------------------------------------------------
#     config = {
#         "document": {
#             "fileType": file_ext,
#             "key": file_id,  # Уникальный идентификатор. Если он изменится, ONLYOFFICE сбросит кэш и скачает файл заново
#             "title": filename,
#             "url": document_url,
#         },
#         "documentType": DOCUMENT_TYPES[file_ext],  # 'word', 'excel' или 'powerpoint'
#         "editorConfig": {
#             "callbackUrl": callback_url,
#             "mode": "view",  # 'edit' — для редактирования, 'view' — только для просмотра
#             "lang": "ru",    # Язык интерфейса редактора
#             "user": {
#                 # Сюда можно передать ID и имя текущего авторизованного пользователя
#                 "id": "user_anonymous",  
#                 "name": "Сотрудник"
#             },
#             "customization": {
#                 # Немного кастомизации для закрытого контура: отключаем обратную связь и чат наружу
#                 "feedback": False,
#                 "forcesave": True,  # Включает возможность принудительного сохранения (кнопка Сохранить)
#             }
#         }
#     }

#     return config


@api_files_router.delete("/{id}")
async def api_delete_file(
    id: str,
    repository: FileRepository = fastapi.Depends(AdminFileRepositoryRequired),
):
    """Удалить файл по идентификатору"""
    await repository.delete(uuid.UUID(id))


@api_files_router.put("")
async def api_upload_file(
    schema: FileSchema = fastapi.Depends(FileSchemaAsForm),
    file: fastapi.UploadFile = fastapi.File(...),
    repository: FileRepository = fastapi.Depends(AdminFileRepositoryRequired),
) -> FileModel:
    """Создать файл"""
    name, ext = os.path.splitext(file.filename)
    if schema.name is None:
        schema.name = name

    CHUNK_SIZE = 1024 * 1024 * 10
    path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + ext)
    async with aiofiles.open(path, "wb") as dst:
        while True:
            data = file.file.read(CHUNK_SIZE)
            if len(data) > 0:
                await dst.write(data)
            else:
                break

    model = await repository.create(
        schema=schema,
        file=path,
        move=True,
    )
    model = await repository.model_from_orm(model)

    return model


@api_files_router.patch("")
async def api_update_file(
    schema: FileSchema = fastapi.Body(FileSchemaAsForm),
    file: Optional[fastapi.UploadFile] = fastapi.File(default=None),
    repository: FileRepository = fastapi.Depends(AdminFileRepositoryRequired),
) -> FileModel:
    """Обновить файл"""
    path: str = None

    if file is not None and file.size > 0:
        name, ext = os.path.splitext(file.filename)
        if schema.name is None:
            schema.name = name

        path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + ext)
        async with aiofiles.open(path, "wb") as dst:
            while True:
                data = file.file.read(4096)
                if len(data) > 0:
                    await dst.write(data)
                else:
                    break

    return await repository.model_from_orm(
        await repository.update(
            schema=schema,
            file=file,
            move=True,
        )
    )


@api_files_router.get("")
async def api_files(
    schema: FileFilterSchema = fastapi.Query(),
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired),
) -> list[FileModel]:
    """Получить список файлов"""
    return await repository.models_from_orm(await repository.values(schema=schema))


@api_files_router.post("")
async def api_files(
    schema: FileFilterSchema = fastapi.Body(),
    repository: FileRepository = fastapi.Depends(FileRepositoryRequired),
) -> list[FileModel]:
    """Получить список файлов"""
    return await repository.models_from_orm(await repository.values(schema=schema))



   



__all__ = [
    "api_files_router",
]
