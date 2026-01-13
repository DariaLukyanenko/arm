from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ================ Enums ================
class ApprovalAction(str, Enum):
    """Действие при согласовании"""
    APPROVE = "approve"
    REJECT = "reject"


class RejectReason(str, Enum):
    """Причина отклонения"""
    INCORRECT = "incorrect"
    INCOMPLETE = "incomplete"
    DUPLICATE = "duplicate"
    OUTDATED = "outdated"


# ================ Request Schemas ================
class ApproveRequest(BaseModel):
    """Запрос на утверждение требования"""
    comment: Optional[str] = Field(None, description="Комментарий к утверждению")


class RejectRequest(BaseModel):
    """Запрос на отклонение требования"""
    comment: str = Field(..., description="Комментарий к отклонению")
    reason: RejectReason = Field(..., description="Причина отклонения")


# ================ Response Schemas ================
class RequirementApprover(BaseModel):
    """Согласование требования"""
    id: UUID
    requirement_id: UUID
    user_id: Optional[UUID] = None
    action: str
    comment: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

