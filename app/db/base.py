# db/base.py

from cloud_sql_python_connector import Connector
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Importar modelos para asegurarnos de que SQLAlchemy los registre
# Ajusta estos imports según donde tengas tus modelos
from .models import users, pressures, evaluations  # <-- agrega los tuyos

Base = declarative_base()

# Conector de Cloud SQL
connector = Connector(enable_iam_auth=False)

def getconn():
    """Crea una conexión usando Cloud SQL Connector (pg8000)."""
    conn = connector.connect(
        settings.CLOUD_SQL_CONNECTION_NAME,
        "pg8000",
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        db=settings.DB_NAME,
    )
    return conn

# SQLAlchemy Engine (sin URL, usa creator)
engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    pool_recycle=1800,
    pool_pre_ping=True,
)

# Sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Crear tablas al iniciar el servidor."""
    Base.metadata.create_all(bind=engine)

def close_connector():
    """Cerrar Cloud SQL Connector al apagar la aplicación."""
    connector.close()
    print("Cloud SQL Connector cerrado.")