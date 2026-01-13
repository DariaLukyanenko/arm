from uuid import UUID

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class Requirement(Base):
    """Требование"""
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(255))
    depth: Mapped[int] = mapped_column(Integer)
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("requirements.id", ondelete="SET NULL"),
        nullable=True
    )

    # Foreign Keys
    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True
    )
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
