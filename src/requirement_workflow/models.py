from uuid import UUID

from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class RequirementWorkflow(Base):
    """Workflow требования - текущий статус и приоритет"""
    requirement_id: Mapped[UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE"),
        unique=True
    )
    
    priority: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default='draft')

