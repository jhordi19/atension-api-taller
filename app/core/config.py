# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
import os

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    # Cloud SQL Connection Name
    CLOUD_SQL_CONNECTION_NAME: str
    
    # Database credentials
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # JWT Configuration
    SECRET_KEY: str
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