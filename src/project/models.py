from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class Project(Base):
    """Проект"""
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))

    # Foreign Keys
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
