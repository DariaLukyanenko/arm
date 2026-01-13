from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ================ Enums ================
class WorkflowStatus(str, Enum):
    """Статус workflow требования"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    ARCHIVED = "archived"


# ================ Request Schemas ================
class WorkflowTransition(BaseModel):
    """Изменение статуса workflow"""
    new_status: WorkflowStatus = Field(..., description="Новый статус")
    comment: Optional[str] = Field(None, description="Комментарий к изменению")


# ================ Response Schemas ================
class RequirementWorkflow(BaseModel):
    """Workflow требования"""
    id: UUID
    requirement_id: UUID
    priority: int = Field(..., ge=1, le=5, description="Приоритет (1-5)")
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class WorkflowStatus(BaseModel):
    """Текущий статус workflow с возможными переходами"""
    id: UUID
    requirement_id: UUID
    requirement_name: str
    priority: int
    status: str
    can_transition_to: list[str] = Field(default_factory=list, description="Доступные статусы для перехода")
    created_at: datetime
    updated_at: datetime


class WorkflowHistoryItem(BaseModel):
    """Элемент истории workflow"""
    id: UUID
    requirement_id: UUID
    prev_workflow_history_id: Optional[UUID] = None
    created_by_user_id: Optional[UUID] = None
    priority: int
    status: str
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class WorkflowHistoryList(BaseModel):
    """История изменений workflow"""
    data: list[WorkflowHistoryItem]

