# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
import os

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    # --- Base de Datos ---
    DATABASE_URL: str = "sqlite:///./app/atension.db"
    
    # Cloud SQL Connection Name
    CLOUD_SQL_CONNECTION_NAME: str = "thermal-outlet-478406-a1:us-central1:hypertension-project-db"
    
    # Credenciales de PostgreSQL
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "jI73480489*"
    DB_NAME: str = "atension_database"
    
    # --- JWT ---
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore",
        case_sensitive=False,
    )
    
    def get_database_url(self) -> str:
        """Retorna la URL de la base de datos según el entorno"""
        # Si estamos en Cloud Run
        if os.getenv("K_SERVICE"):
            return (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@/{self.DB_NAME}?host=/cloudsql/{self.CLOUD_SQL_CONNECTION_NAME}"
            )
        # Local - usar SQLite o PostgreSQL local
        return self.DATABASE_URL

@lru_cache
def get_settings() -> "Settings":
    return Settings()

settings = get_settings()