from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class Requirement(Base):
    """Требование"""
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(255))
    depth: Mapped[str] = mapped_column(String(255))
    description_text: Mapped[str] = mapped_column(String(1023))

    # Foreign Keys
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    # requirement_group_id: Mapped[UUID] = mapped_column(ForeignKey())  TODO дописать как появится модель
