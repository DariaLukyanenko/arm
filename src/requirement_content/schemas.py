from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ================ Request Schemas ================
class RequirementContentUpdate(BaseModel):
    """Обновление содержимого требования"""
    development_basis: Optional[str] = Field(None, description="Основание для разработки")
    development_purpose: Optional[str] = Field(None, description="Цель разработки")
    description_text: Optional[str] = Field(None, description="Текст описания")
    acceptance_criteria: Optional[str] = Field(None, description="Критерии приемки")
    document_requires: Optional[str] = Field(None, description="Документальные требования")


# ================ Response Schemas ================
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

