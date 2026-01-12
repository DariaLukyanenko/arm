from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class User(Base):
    """Пользователь"""
    external_id: Mapped[int] = mapped_column(autoincrement=True, unique=True)
    status: Mapped[str] = mapped_column(String(255))
