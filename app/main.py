# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import base as db_base
from app.api.endpoints import users, auth, evaluations, pressures
from app.db.update_enum import update_bp_category_enum

app = FastAPI(
    title="aTensión Backend API",
    description="API para la aplicación móvil de valoración de riesgo de hipertensión arterial.",
    version="1.0.0"
)

# CORS (Ajusta allow_origins en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- STARTUP EVENT (IMPORTANTE PARA CLOUD RUN) ----------
@app.on_event("startup")
def on_startup():
    """
    Inicializa las tablas y actualiza enums cuando el servidor ARRANCA,
    no antes (Cloud Run lo requiere).
    """
    db_base.init_db()
    update_bp_category_enum()


# ---------- ROUTERS ----------
api_prefix = "/api/v1"

app.include_router(users.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(evaluations.router, prefix=api_prefix)
app.include_router(pressures.router, prefix=api_prefix)


# ---------- HEALTH & ROOT ----------
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de aTensión"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@app.on_event("shutdown")
def shutdown_event():
    db_base.close_connector()
    print("Conexión del conector cerrada.")