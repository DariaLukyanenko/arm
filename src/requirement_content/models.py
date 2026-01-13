from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class RequirementContent(Base):
    """Содержимое требования"""
    requirement_id: Mapped[UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE"),
        unique=True
    )
    
    # Все поля Text и nullable
    development_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    development_purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_requires: Mapped[str | None] = mapped_column(Text, nullable=True)

