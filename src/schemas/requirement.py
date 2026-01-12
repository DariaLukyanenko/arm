"""
Pydantic схемы для требований
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class RequirementType(str, Enum):
    functional = "functional"
    non_functional = "non-functional"
    business = "business"


class WorkflowStatus(str, Enum):
    draft = "draft"
    review = "review"
    approved = "approved"
    rejected = "rejected"
    implemented = "implemented"
    verified = "verified"
    archived = "archived"


class DependencyType(str, Enum):
    blocks = "blocks"
    depends_on = "depends_on"
    related_to = "related_to"
    duplicates = "duplicates"
    refines = "refines"


class TestStatus(str, Enum):
    passed = "passed"
    failed = "failed"
    blocked = "blocked"
    not_executed = "not_executed"


# Base schemas
class RequirementContentBase(BaseModel):
    """Базовая схема для содержимого требования"""
    development_basis: Optional[str] = None
    development_purpose: Optional[str] = None
    description_text: str
    acceptance_criteria: Optional[str] = None
    document_requires: Optional[str] = None


class RequirementContentCreate(RequirementContentBase):
    """Схема для создания содержимого требования"""
    pass


class RequirementContentUpdate(RequirementContentBase):
    """Схема для обновления содержимого требования"""
    pass


class RequirementContent(RequirementContentBase):
    """Схема содержимого требования"""
    id: int
    requirement_id: int
    created_at: datetime
    created_by_user_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RequirementWorkflowBase(BaseModel):
    """Базовая схема для workflow"""
    priority: int = Field(default=3, ge=1, le=5)
    status: WorkflowStatus = WorkflowStatus.draft


class RequirementWorkflow(RequirementWorkflowBase):
    """Схема workflow требования"""
    id: int
    requirement_content_id: int
    created_at: datetime
    created_by_user_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RequirementBase(BaseModel):
    """Базовая схема требования"""
    name: str = Field(..., max_length=255)
    type: RequirementType
    parent_id: Optional[int] = None


class RequirementCreate(RequirementBase):
    """Схема для создания требования"""
    project_id: int
    content: RequirementContentCreate


class RequirementUpdate(BaseModel):
    """Схема для обновления требования"""
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[RequirementType] = None


class Requirement(RequirementBase):
    """Схема требования"""
    id: int
    project_id: int
    created_at: datetime
    created_by_user_id: int
    path: Optional[str] = None
    depth: int
    requirement_group_id: Optional[int] = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class RequirementFull(Requirement):
    """Полная схема требования с контентом и workflow"""
    content: Optional[RequirementContent] = None
    workflow: Optional[RequirementWorkflow] = None


class RequirementListResponse(BaseModel):
    """Схема списка требований"""
    data: List[RequirementFull]
    pagination: Optional[dict] = None


# Dependency schemas
class DependencyBase(BaseModel):
    """Базовая схема зависимости"""
    target_requirement_id: int
    type: DependencyType
    strength: int = Field(default=3, ge=1, le=5)
    description: Optional[str] = None


class DependencyCreate(DependencyBase):
    """Схема для создания зависимости"""
    pass


class Dependency(DependencyBase):
    """Схема зависимости"""
    id: int
    source_requirement_id: int
    source_requirement_group_id: Optional[int] = None
    target_requirement_group_id: Optional[int] = None
    created_at: datetime
    created_by_user_id: int

    model_config = ConfigDict(from_attributes=True)


class DependencyList(BaseModel):
    """Схема списка зависимостей"""
    incoming: List[Dependency] = []
    outgoing: List[Dependency] = []


# Test Coverage schemas
class TestCoverageBase(BaseModel):
    """Базовая схема покрытия тестами"""
    test_case_version_id: str
    test_case_status: TestStatus


class TestCoverageUpdate(TestCoverageBase):
    """Схема для обновления покрытия тестами"""
    pass


class TestCoverage(TestCoverageBase):
    """Схема покрытия тестами"""
    id: int
    requirement_id: int
    created_at: datetime
    created_by_user_id: int
    execution_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Traceability schemas
class TraceabilityItem(BaseModel):
    """Элемент трассируемости"""
    requirement_id: int
    requirement_name: str


class TraceabilityMatrix(BaseModel):
    """Матрица трассируемости"""
    requirement_id: int
    requirement_name: str
    source: List[TraceabilityItem] = []
    target: List[TraceabilityItem] = []


# Report schemas
class KPIDashboard(BaseModel):
    """Дашборд KPI"""
    period: dict
    metrics: dict


class RequirementsReport(BaseModel):
    """Отчет по требованиям"""
    project_id: int
    project_name: str
    generated_at: datetime
    requirements: List[RequirementFull]
    summary: dict


class WorkflowTransition(BaseModel):
    """Схема для изменения статуса workflow"""
    new_status: WorkflowStatus
    comment: Optional[str] = None

