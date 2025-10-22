# db/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True, future=True)
print(f"[DEBUG] DATABASE_URL en uso -> {engine.url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import tardío para evitar import circular
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)