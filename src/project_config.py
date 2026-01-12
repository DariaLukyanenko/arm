from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    APP_PORT: int
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_SCHEMA: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_APP_USER: str
    POSTGRES_APP_PASSWORD: str
    DB_ECHO_LOG: bool = False
    PROJECT_NAME: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 21600
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def database_url(self) -> Optional[str]:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()  # noqa
