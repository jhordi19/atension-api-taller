# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
import os

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    # Cloud SQL Connection Name
    CLOUD_SQL_CONNECTION_NAME: str = "thermal-outlet-478406-a1:us-central1:hypertension-project-db"

    DB_USER: str = "postgres"
    DB_PASSWORD: str = "jI73480489*"
    DB_NAME: str = "atension_database"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore",
        case_sensitive=False,
    )

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
