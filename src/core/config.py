"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Приложение
    APP_PORT: int = 8000
    PROJECT_NAME: str = "Автоматизированная система управления требованиями (АСУТр)"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/v1"
    
    # База данных  
    POSTGRES_HOST: str = "dev-postgresql"  # Имя контейнера в docker-compose
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_SCHEMA: str
    POSTGRES_APP_USER: str
    POSTGRES_APP_PASSWORD: str
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # SSO/LDAP (пока заглушки)
    SSO_ENABLED: bool = False
    SSO_URL: Optional[str] = None
    LDAP_URL: Optional[str] = None
    
    @property
    def database_url(self) -> str:
        """Строка подключения к БД"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_APP_USER}:{self.POSTGRES_APP_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def database_url_sync(self) -> str:
        """Синхронная строка подключения к БД (для Alembic)"""
        return (
            f"postgresql://{self.POSTGRES_APP_USER}:{self.POSTGRES_APP_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

