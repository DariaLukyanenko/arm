"""
API Router v1
"""
from fastapi import APIRouter

from api.v1.endpoints import requirements, dependencies, reports, projects

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(projects.router)
api_router.include_router(requirements.router)
api_router.include_router(dependencies.router)
api_router.include_router(reports.router)

