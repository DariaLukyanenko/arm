import re
from datetime import datetime

import inflect
from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now()
    )

    _inflect_engine = inflect.engine()
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Конвертируем CamelCase в snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

        # Плюрализуем последнее слово
        words = name.split('_')
        words[-1] = str(cls._inflect_engine.plural(words[-1]))  # noqa

        return '_'.join(words)
