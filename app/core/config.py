# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    # Cloud SQL Connection Name
    CLOUD_SQL_CONNECTION_NAME: str = (
        "thermal-outlet-478406-a1:us-central1:hypertension-project-db"
    )
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "jI73480489*"
    DB_NAME: str = "atension_database"

    # Conexión directa por IP pública
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:jI73480489*@34.172.110.118:5432/atension_database"
    )

    # JWT
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
