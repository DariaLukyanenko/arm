from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ================ Enums ================
class RequirementType(str, Enum):
    """Тип требования"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"
    BUSINESS = "business"


# ================ Request Schemas ================
class RequirementCreate(BaseModel):
    """Создание требования"""
    project_id: UUID = Field(..., description="ID проекта")
    name: str = Field(..., max_length=255, description="Название требования")
    type: RequirementType = Field(..., description="Тип требования")
    parent_id: Optional[UUID] = Field(None, description="ID родительского требования для иерархии")
    
    # Содержимое требования (будет создано в RequirementContent)
    development_basis: Optional[str] = Field(None, description="Основание для разработки")
    development_purpose: Optional[str] = Field(None, description="Цель разработки")
    description_text: Optional[str] = Field(None, description="Текст описания")
    acceptance_criteria: Optional[str] = Field(None, description="Критерии приемки")
    document_requires: Optional[str] = Field(None, description="Документальные требования")


class RequirementUpdate(BaseModel):
    """Обновление требования"""
    name: Optional[str] = Field(None, max_length=255, description="Название требования")
    type: Optional[RequirementType] = Field(None, description="Тип требования")


# ================ Response Schemas ================
class Requirement(BaseModel):
    """Базовая информация о требовании"""
    id: UUID
    project_id: Optional[UUID] = None
    name: str
    type: str
    path: str
    depth: int
    parent_id: Optional[UUID] = None
    created_by_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class RequirementContent(BaseModel):
    """Содержимое требования"""
    id: UUID
    requirement_id: UUID
    development_basis: Optional[str] = None
    development_purpose: Optional[str] = None
    description_text: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    document_requires: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class RequirementWorkflow(BaseModel):
    """Workflow требования"""
    id: UUID
    requirement_id: UUID
    priority: int = Field(..., ge=1, le=5, description="Приоритет (1-5)")
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class RequirementFull(BaseModel):
    """Полная информация о требовании с содержимым и workflow"""
    requirement: Requirement
    content: Optional[RequirementContent] = None
    workflow: Optional[RequirementWorkflow] = None


class RequirementListResponse(BaseModel):
    """Список требований"""
    data: list[RequirementFull]


# ================ Content History ================
class ContentHistoryItem(BaseModel):
    """Элемент истории содержимого"""
    id: UUID
    requirement_id: UUID
    prev_content_history_id: Optional[UUID] = None
    created_by_user_id: Optional[UUID] = None
    development_basis: Optional[str] = None
    development_purpose: Optional[str] = None
    description_text: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    document_requires: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ContentHistoryList(BaseModel):
    """История изменений содержимого"""
    data: list[ContentHistoryItem]


# ================ Legacy (для совместимости) ================
class RequirementRequest(BaseModel):
    """Устаревшая схема - для совместимости"""
    project_id: UUID = Field(description='ID проекта')
    name: str = Field(description='Название')
    description_text: str = Field(description='Описание')


class RequirementResponse(BaseModel):
    """Устаревшая схема - для совместимости"""
    id: UUID = Field(description='ID записи')
    project_id: UUID = Field(description='ID проекта')
    name: str = Field(description='Название')
    description_text: str = Field(description='Описание')
