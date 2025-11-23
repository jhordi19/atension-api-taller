# db/base.py

from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Primero define Base
Base = declarative_base()

# Cloud SQL Connector
connector = Connector(enable_iam_auth=False)

def getconn():
    conn = connector.connect(
        settings.CLOUD_SQL_CONNECTION_NAME,
        "pg8000",
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        db=settings.DB_NAME,
    )
    return conn

engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
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


# IMPORTA MODELOS AL FINAL
from db import models  # noqa

def init_db():
    Base.metadata.create_all(bind=engine)

def close_connector():
    connector.close()
    print("Cloud SQL Connector cerrado.")