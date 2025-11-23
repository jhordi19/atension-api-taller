# main.py corregido
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware  # ✅ Importa el middleware

from db import base as db_base
from api.endpoints import users, auth, evaluations, pressures, ratings
from db.update_enum import update_bp_category_enum
from core.log_config import setup_logging

app = FastAPI(
    title="aTensión Backend API",
    description="API para la aplicación móvil de valoración de riesgo de hipertensión arterial.",
    version="1.0.0",
)

# ✅ Añade el middleware GZip antes o después del CORS, como prefieras
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    db_base.init_db()
    update_bp_category_enum()
    setup_logging()


api_prefix = "/api/v1"

app.include_router(users.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(evaluations.router, prefix=api_prefix)
app.include_router(pressures.router, prefix=api_prefix)
app.include_router(ratings.router, prefix=api_prefix, tags=["ratings"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de aTensión"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.on_event("shutdown")
def shutdown_event():
    print("Apagando la aplicación...")
