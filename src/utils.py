from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status

from src.project_config import settings


class JWTHandler:
    """Класс для работы с JWT токенами."""

    @staticmethod
    def _create_access_token(data: dict) -> str:
        """Создает access токен.

        Args:
            data: Данные для включения в токен

        Returns:
            JWT токен
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({'exp': expire, 'type': 'access'})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """Декодирует JWT токен.

        Args:
            token: JWT токен

        Returns:
            Декодированные данные

        Raises:
            HTTPException: Если токен невалидный или истек
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Токен истек',
            ) from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Невалидный токен',
            ) from e

    @staticmethod
    def create_token(data: dict) -> dict:
        """Создает access токен.

        Args:
            data: Данные для включения в токен

        Returns:
            Словарь с access_token, token_type и expires_in
        """
        access_token = JWTHandler._create_access_token(data)

        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
