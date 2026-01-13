"""Перечисления (Enums) для базы данных"""
from enum import Enum


class UserStatus(str, Enum):
    """Статус пользователя"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class RequirementType(str, Enum):
    """Тип требования"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"
    BUSINESS = "business"


class WorkflowStatus(str, Enum):
    """Статус workflow требования"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    ARCHIVED = "archived"


class ApprovalAction(str, Enum):
    """Действие при согласовании"""
    APPROVE = "approve"
    REJECT = "reject"


class RejectReason(str, Enum):
    """Причина отклонения требования"""
    INCORRECT = "incorrect"
    INCOMPLETE = "incomplete"
    DUPLICATE = "duplicate"
    OUTDATED = "outdated"

