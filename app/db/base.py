# db/base.py

import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

Base = declarative_base()

# Conexión directa a Cloud SQL por IP pública
engine = sqlalchemy.create_engine(
    settings.DATABASE_URL,
    pool_recycle=1800,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.db import models  # noqa


def init_db():
    Base.metadata.create_all(bind=engine)
