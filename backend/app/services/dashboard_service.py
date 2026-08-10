from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.trabajo import Trabajo, EstadoTrabajo
from app.models.servicio import Servicio
from app.models.tecnico import Tecnico


def _rango_periodo(periodo: str) -> tuple[date, date]:
    hoy = date.today()
    if periodo == "semana":
        return hoy - timedelta(days=6), hoy
    if periodo == "mes":
        return hoy.replace(day=1), hoy
    if periodo == "anio":
        return hoy.replace(month=1, day=1), hoy
    raise ValueError("periodo debe ser 'semana', 'mes' o 'anio'")


def kpis(db: Session, periodo: str) -> dict:
    desde, hasta = _rango_periodo(periodo)
    base = db.query(Trabajo).filter(
        Trabajo.estado == EstadoTrabajo.realizado,
        Trabajo.fecha_realizado >= desde,
        Trabajo.fecha_realizado <= hasta,
    )

    n = base.count()
    revenue = base.with_entities(func.coalesce(func.sum(Trabajo.monto), 0)).scalar() or 0
    costo = base.with_entities(func.coalesce(func.sum(Trabajo.costo), 0)).scalar() or 0
    duracion_prom = base.with_entities(func.coalesce(func.avg(Trabajo.duracion_min), 0)).scalar() or 0

    revenue = float(revenue)
    costo = float(costo)
    ganancia = revenue - costo

    return {
        "periodo": periodo,
        "desde": desde,
        "hasta": hasta,
        "trabajos_realizados": n,
        "facturacion": revenue,
        "costo": costo,
        "ganancia_neta": ganancia,
        "margen_pct": (ganancia / revenue * 100) if revenue else 0,
        "ticket_promedio": (revenue / n) if n else 0,
        "duracion_promedio_min": float(duracion_prom),
    }


def por_servicio(db: Session, periodo: str) -> list[dict]:
    desde, hasta = _rango_periodo(periodo)
    filas = (
        db.query(Servicio.nombre, Servicio.color, func.count(Trabajo.id), func.coalesce(func.sum(Trabajo.monto), 0))
        .join(Trabajo, Trabajo.servicio_id == Servicio.id)
        .filter(
            Trabajo.estado == EstadoTrabajo.realizado,
            Trabajo.fecha_realizado >= desde,
            Trabajo.fecha_realizado <= hasta,
        )
        .group_by(Servicio.nombre, Servicio.color)
        .all()
    )
    return [
        {"servicio": nombre, "color": color, "trabajos": cantidad, "facturacion": float(monto)}
        for nombre, color, cantidad, monto in filas
    ]


def por_tecnico(db: Session, periodo: str) -> list[dict]:
    desde, hasta = _rango_periodo(periodo)
    filas = (
        db.query(Tecnico.nombre, func.count(Trabajo.id), func.coalesce(func.sum(Trabajo.monto), 0))
        .join(Trabajo, Trabajo.tecnico_id == Tecnico.id)
        .filter(
            Trabajo.estado == EstadoTrabajo.realizado,
            Trabajo.fecha_realizado >= desde,
            Trabajo.fecha_realizado <= hasta,
        )
        .group_by(Tecnico.nombre)
        .order_by(func.coalesce(func.sum(Trabajo.monto), 0).desc())
        .all()
    )
    return [
        {"tecnico": nombre, "trabajos": cantidad, "facturacion": float(monto)}
        for nombre, cantidad, monto in filas
    ]
