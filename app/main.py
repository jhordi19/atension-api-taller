# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import base as db_base
from .api.endpoints import users, auth, evaluations, pressures
from .db.update_enum import update_bp_category_enum

# Crea las tablas en la base de datos (si no existen)
# En un entorno de producción, manejarías esto con migraciones (ej. Alembic)
db_base.init_db()

# Actualizar el enum bp_category si es necesario
update_bp_category_enum()

app = FastAPI(
    title="aTensión Backend API",
    description="API para la aplicación móvil de valoración de riesgo de hipertensión arterial.",
    version="1.0.0"
)

# Configurar CORS para desarrollo local
# NOTA: En producción, especifica los orígenes exactos en lugar de usar ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de los endpoints
api_prefix = "/api/v1"

app.include_router(users.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(evaluations.router, prefix=api_prefix)
app.include_router(pressures.router, prefix=api_prefix)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de aTensión"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


#venv\Scripts\activate
#uvicorn app.main:app --reload
#uvicorn app.main:app --reload --host 0.0.0.0 --port 8000