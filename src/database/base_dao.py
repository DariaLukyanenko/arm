from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Unpack
from uuid import UUID

from sqlalchemy import select, delete, insert, update, and_, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовая модель для всех таблиц"""
    __abstract__ = True

    id: Mapped[int | UUID] = mapped_column(primary_key=True)


ModelType = TypeVar("ModelType", bound=Base)


class BaseDAO(Generic[ModelType]):
    """Базовый класс для работы с БД"""

    options:  List[Any] = []
    model: Type[ModelType]

    @classmethod
    async def create(
            cls,
            session: AsyncSession,
            **values: Unpack[Dict[str, Any]]
    ) -> Optional[ModelType]:
        """Создаёт новую запись в базе данных.

        Параметры:
            session - асинхронная сессия SQLAlchemy
            values - значения для создания записи.
        Возвращает:
            Созданный объект.
            Если запись не была создана, выбрасывается исключение.
        """
        query = insert(cls.model).values(**values).returning(
            cls.model).options(*cls.options)

        result = await session.execute(query)
        return result.scalar_one()

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        obj_id: int | UUID
    ) -> Optional[ModelType]:
        """Получает запись по её первичному ключу.

        Параметры:
            session - асинхронная сессия SQLAlchemy
            obj_id - идентификатор записи.
        Возвращает:
            Запись, найденную по pk. Если запись не найдена,
            выбрасывается исключение.
        """
        query = select(cls.model).where(cls.model.id == obj_id).options(
            *cls.options)

        result = await session.execute(query)
        return result.scalar_one()

    @classmethod
    async def update(
            cls,
            session: AsyncSession,
            obj_id: int | UUID,
            **values: Unpack[Dict[str, Any]]
    ) -> Optional[ModelType]:
        """Обновляет запись по её идентификатору.

        Параметры:
            session - асинхронная сессия SQLAlchemy
            obj_id - идентификатор записи
            values - поля и их новые значения для обновления.
        Возвращает:
            Обновлённый объект.
            Если запись не найдена, выбрасывается исключение.
        """
        query = (
            update(cls.model)
            .where(cls.model.id == obj_id)
            .values(**values)
            .returning(cls.model)
        ).options(*cls.options)

        result = await session.execute(query)
        return result.scalar_one()

    @classmethod
    async def delete(
        cls,
        session: AsyncSession,
        obj_id: int | UUID
    ) -> Optional[ModelType]:
        """
        Удаляет запись по ID.

        Параметры:
            session - асинхронная сессия SQLAlchemy
            obj_id - идентификатор записи.
        Возвращает:
            Удаленный объект.
            Если запись не была удалена, выбрасывается исключение.
        """
        query = (
            delete(cls.model)
            .where(cls.model.id == obj_id)
            .returning(cls.model)
        )

        result = await session.execute(query)
        return result.scalar_one()

    @classmethod
    async def get_by(
            cls,
            session: AsyncSession,
            base_query: Optional[Select] = None,
            **filters: Unpack[Dict[str, Any]],
    ) -> Optional[ModelType] | List[ModelType]:
        """Получает записи по произвольным фильтрам.

        Параметры:
            session - асинхронная сессия SQLAlchemy
            base_query - базовый запрос для выборки
            **filters - пары поле=значение для фильтрации

        Возвращает:
            Список объектов (может быть пустой)
        """
        query = base_query if base_query is not None else select(
            cls.model).options(*cls.options)

        filter_conditions = []
        for field_name, value in filters.items():
            if not hasattr(cls.model, field_name):
                raise ValueError(
                    f"Модель {cls.model.__name__} не имеет поля '{field_name}'"
                )
            field = getattr(cls.model, field_name)
            if value is None:
                filter_conditions.append(field.is_(None))
            elif value is not None:
                filter_conditions.append(field == value)

        if filter_conditions:
            query = query.where(and_(*filter_conditions))

        result = await session.execute(query)
        return list(result.scalars().all())
