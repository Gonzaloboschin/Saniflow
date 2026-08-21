import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers import clientes, servicios, tecnicos, contratos, trabajos, interacciones, dashboard, importacion

# Sin esto, los logger.info()/logger.exception() de los servicios (ej.
# notificaciones_service) quedan silenciados — Python no muestra nada por
# debajo de WARNING si nadie configura el logging al arrancar.
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

app = FastAPI(
    title=settings.app_name,
    description="API de gestión de trabajos y clientes para empresa de desinfecciones.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router)
app.include_router(servicios.router)
app.include_router(tecnicos.router)
app.include_router(contratos.router)
app.include_router(trabajos.router)
app.include_router(interacciones.router)
app.include_router(dashboard.router)
app.include_router(importacion.router)


@app.get("/health", tags=["sistema"])
def health():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}
