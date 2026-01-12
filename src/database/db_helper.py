from typing import Annotated

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from src.project_config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=echo
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            expire_on_commit=False
        )

    async def get_db_session(self):
        from sqlalchemy import exc

        session: AsyncSession = self.session_factory()
        try:
            yield session
            await session.commit()

        except exc.NoResultFound as e:
            await session.rollback()
            raise HTTPException(
                status_code=404, detail='Объект c данным id не найден'
            ) from e

        except exc.IntegrityError as e:
            await session.rollback()
            error_message = str(e.orig)

            # Обработка нарушения внешнего ключа
            if 'ForeignKeyViolationError' in error_message:
                raise HTTPException(
                    status_code=404,
                    detail='Связанный объект не найден'
                ) from e

            # Обработка нарушения уникальности
            elif 'UniqueViolationError' in error_message:
                raise HTTPException(
                    status_code=409,
                    detail='Объект с такими данными уже существует'
                ) from e

            # Другие ошибки целостности
            else:
                raise HTTPException(
                    status_code=400,
                    detail='Нарушение ограничения целостности данных'
                ) from e

        except exc.SQLAlchemyError as error:
            await session.rollback()
            print(f'SQLAlchemy error: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Произошла ошибка при обработке запроса',
            )
        finally:
            await session.close()


db_helper = DatabaseHelper(settings.database_url, settings.DB_ECHO_LOG)

SessionDep = Annotated[AsyncSession, Depends(db_helper.get_db_session)]
