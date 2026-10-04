from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from endpoints import *

from settings import SETTING_AUTH, SETTING_CORS
from services.database import database_lifespan
from utils.service.authentication import init_auth_fastapi_backend

app = FastAPI(lifespan=database_lifespan)
init_auth_fastapi_backend(
    app=app,
    setting=SETTING_AUTH,
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")
# API
app.include_router(api_file_tags_router, prefix="/api/tags", tags=["Tags"])
app.include_router(api_files_router, prefix="/api/files", tags=["Files"])
app.include_router(api_file_types_router, prefix="/api/types", tags=["File-Types"])
app.include_router(api_search_queries_router, prefix="/api/search_queries", tags=["Search-Queries"])
app.include_router(base_router, tags=["Pages"])
app.include_router(files_router, prefix="/files", tags=["Pages"])
app.include_router(api_graph_router, prefix="/api/graph", tags=["Graph"])


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=SETTING_CORS.allow_origins,
#     allow_credentials=SETTING_CORS.allow_credentials,
#     allow_methods=SETTING_CORS.allow_methods,
#     allow_headers=SETTING_CORS.allow_headers,
# )

# Список строго разрешенных локальных адресов (БЕЗ использования звездочки '*')
ALLOWED_ORIGINS = {
    "http://10.10.10.1:8080",
    "null"
}

# Домен по умолчанию на случай, если браузер скрыл заголовок Origin или прислал "null"
DEFAULT_ORIGIN = "http://10.10.10.1:8080"

@app.middleware("http")
async def partial_content_cors_middleware(request: Request, call_next):
    # работаем только с API для всех остальных запросов пропускаем 
    if not request.url.path.startswith("/api"):
        return await call_next(request)

    # Читаем входящий Origin от браузера
    request_origin = request.headers.get("Origin")
    if request_origin in ALLOWED_ORIGINS:
        cors_origin = request_origin
    
    elif not request_origin:
        # Если заголовка нет вообще (Same-Origin запрос), 
        # отдаем дефолтный фронтенд, чтобы подстраховать JS
        cors_origin = DEFAULT_ORIGIN    
    else:
        cors_origin = ""  # Блокируем чужие вредоносные домены

    cors_headers = {
        "Access-Control-Allow-Origin": cors_origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        # Обязательно разрешаем входящий заголовок "Range", иначе статус 206 заблокируется на входе
        "Access-Control-Allow-Headers": "X-Requested-With, Content-Type, Accept, Origin, Authorization, Range",
        # КРИТИЧЕСКИ ВАЖНО ДЛЯ СТАТУСА 206: Выносим заголовки Range наружу, 
        # чтобы JavaScript-плеер внутри фрейма имел право прочитать разметку кусков файла в памяти
        "Access-Control-Expose-Headers": "Content-Length, Content-Range, Content-Disposition, Accept-Ranges"
    }

    # Браузер всегда отправляет OPTIONS перед тем, как начать качать файл по кусочкам (Range)
    if request.method == "OPTIONS":
        response = Response(status_code=204)
        for key, value in cors_headers.items():
            response.headers[key] = value
        return response

    response = await call_next(request)
    
    # 3. ПРИНУДИТЕЛЬНО НАКЛАДЫВАЕМ CORS НА ОТВЕТ СЕРВЕРА
    # Благодаря этому циклу, даже если FastAPI вернул StreamingResponse со статусом 206,
    # заголовки CORS гарантированно встроятся в пакет данных и не потеряются.
    for key, value in cors_headers.items():
        response.headers[key] = value

    return response
