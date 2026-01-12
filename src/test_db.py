"""
Тест подключения к БД
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, text
from db.session import AsyncSessionLocal
from models.person import Person
from core.config import settings


async def test_connection():
    print(f"Database URL: {settings.database_url}")
    print(f"Connecting to {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f"Database: {settings.POSTGRES_DB}")
    print(f"Schema: {settings.POSTGRES_SCHEMA}")
    
    async with AsyncSessionLocal() as session:
        # Проверка простого запроса
        result = await session.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"\nPostgreSQL version: {version}")
        
        # Проверка доступа к схеме
        result = await session.execute(
            text(f"SET search_path TO {settings.POSTGRES_SCHEMA}, public")
        )
        
        # Получение данных из person
        result = await session.execute(select(Person).limit(5))
        persons = result.scalars().all()
        print(f"\nFound {len(persons)} persons:")
        for person in persons:
            print(f"  - ID: {person.id}, External ID: {person.external_id}, Status: {person.status}")


if __name__ == "__main__":
    asyncio.run(test_connection())

