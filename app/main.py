# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import base as db_base
from .api.endpoints import users, auth, evaluations

# Crea las tablas en la base de datos (si no existen)
# En un entorno de producción, manejarías esto con migraciones (ej. Alembic)
db_base.init_db()

app = FastAPI(
    title="aTensión Backend API",
    description="API para la aplicación móvil de valoración de riesgo de hipertensión arterial.",
    version="1.0.0"
)

# Configurar CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://192.168.1.100:3000",  # ← Añadir tu IP
        "http://192.168.1.100:8080",  # ← Añadir tu IP
        "*", 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de los endpoints
api_prefix = "/api/v1"

app.include_router(users.router, prefix=f"{api_prefix}/users", tags=["Users"])
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Auth"])
app.include_router(evaluations.router, prefix=f"{api_prefix}/evaluations", tags=["Evaluations"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de aTensión"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


#venv\Scripts\activate
#uvicorn app.main:app --reload
#uvicorn app.main:app --reload --host 0.0.0.0 --port 8000