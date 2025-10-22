# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    # --- Base de Datos ---
    # Lee DATABASE_URL desde .env. Si no existe, usa SQLite por defecto.
    DATABASE_URL: str = "sqlite:///./app/atension.db"

    # --- JWT ---
    # Lee las variables de seguridad desde .env.
    # Los valores por defecto son solo para desarrollo si .env no está.
    SECRET_KEY: str = "clave-secreta-por-defecto-cambiarla"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pydantic v2
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore",
        case_sensitive=False,
    )

@lru_cache
def get_settings() -> "Settings":
    return Settings()

# Creamos una única instancia global de la configuración.
# Todos los demás archivos importarán esta instancia 'settings'.
settings = get_settings()