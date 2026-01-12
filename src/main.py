"""
Главный модуль приложения АСУТр
"""
import sys
from pathlib import Path
import yaml

# Добавляем src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from core.config import settings
from api.v1.api import api_router

# Загружаем swagger.yaml
swagger_path = Path(__file__).parent.parent / "resources" / "swagger.yaml"
with open(swagger_path, "r", encoding="utf-8") as f:
    swagger_spec = yaml.safe_load(f)

# Создаем приложение
app = FastAPI(
    title=swagger_spec["info"]["title"],
    description=swagger_spec["info"]["description"],
    version=swagger_spec["info"]["version"],
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Hello! This is ARMS service!",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "ok"}


# Подключаем роутеры API v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


def custom_openapi():
    """Кастомная OpenAPI схема из swagger.yaml"""
    if app.openapi_schema:
        return app.openapi_schema
    
    # Используем swagger.yaml как базу
    openapi_schema = swagger_spec.copy()
    
    # Обновляем servers для локального развертывания
    openapi_schema["servers"] = [
        {"url": f"http://localhost:{settings.APP_PORT}{settings.API_V1_PREFIX}", "description": "Local development"},
        {"url": f"http://localhost:{settings.APP_PORT}", "description": "Local development (root)"},
    ] + openapi_schema.get("servers", [])
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Переопределяем схему OpenAPI
app.openapi = custom_openapi
