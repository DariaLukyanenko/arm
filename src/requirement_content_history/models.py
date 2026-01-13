from uuid import UUID

from sqlalchemy import ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class ReqContentHistory(Base):
    """История изменений содержимого требования"""
    requirement_id: Mapped[UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE")
    )
    prev_content_history_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("req_content_histories.id", ondelete="SET NULL"),
        nullable=True
    )
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Snapshot - копии всех полей содержимого
    development_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    development_purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_requires: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # True для последней версии
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

