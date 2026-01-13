from uuid import UUID

from sqlalchemy import ForeignKey, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class ReqWorkflowHistory(Base):
    """История изменений workflow требования"""
    requirement_id: Mapped[UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE")
    )
    prev_workflow_history_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("req_workflow_histories.id", ondelete="SET NULL"),
        nullable=True
    )
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Snapshot - копии полей workflow
    priority: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50))
    
    # True для последней версии
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

