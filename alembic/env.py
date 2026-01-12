import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from alembic.operations import ops
from alembic.autogenerate import rewriter

from src.project_config import settings
# Импортируем модели
from src.database.models import Base

# this is the Alembic Config object
config = context.config

# Читаем URL из переменных окружения
database_url = os.getenv(
    "DATABASE_URL",
    settings.database_url
)
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Создаём rewriter для изменения порядка колонок
writer = rewriter.Rewriter()


@writer.rewrites(ops.CreateTableOp)
def order_columns(context, revision, op):
    """Переставляет базовые колонки в начало"""
    base_columns = ['id', 'created_at', 'updated_at']

    # Разделяем колонки на базовые и остальные
    ordered = []
    other = []

    for col in op.columns:
        if col.name in base_columns:
            ordered.append((base_columns.index(col.name), col))
        else:
            other.append(col)

    # Сортируем базовые колонки по нужному порядку
    ordered.sort(key=lambda x: x[0])

    # Собираем: сначала базовые, потом остальные
    op.columns = [col for _, col in ordered] + other

    return op


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=writer,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполняем миграции в синхронном контексте."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=writer,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создаем async engine и запускаем миграции."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()