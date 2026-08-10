from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

Periodo = Literal["semana", "mes", "anio"]


@router.get("/kpis")
def kpis(periodo: Periodo = "mes", db: Session = Depends(get_db)):
    return dashboard_service.kpis(db, periodo)


@router.get("/por-servicio")
def por_servicio(periodo: Periodo = "mes", db: Session = Depends(get_db)):
    return dashboard_service.por_servicio(db, periodo)


@router.get("/por-tecnico")
def por_tecnico(periodo: Periodo = "mes", db: Session = Depends(get_db)):
    return dashboard_service.por_tecnico(db, periodo)
