"""
Базовые схемы для API
"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """Схема ошибки"""
    error: str
    message: str
    details: Optional[Any] = None
    timestamp: datetime = datetime.utcnow()


class MessageResponse(BaseModel):
    """Схема простого сообщения"""
    message: str


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page: int = 1
    limit: int = 20


class PaginationMeta(BaseModel):
    """Метаданные пагинации"""
    page: int
    limit: int
    total: int
    pages: int

