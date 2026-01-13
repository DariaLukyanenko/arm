from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class ProjectCreateStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"


class ProjectUpdateStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


# === Request Schemas ===
class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: ProjectCreateStatus = ProjectCreateStatus.ACTIVE


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectUpdateStatus] = None


# === Response Schemas ===
class Project(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    status: ProjectStatus
    created_by_user_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class ProjectList(BaseModel):
    data: list[Project]
