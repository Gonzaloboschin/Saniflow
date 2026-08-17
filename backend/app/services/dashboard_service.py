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

    # Eventual = sin contrato detrás; Fijo = nace de un contrato con frecuencia periódica.
    eventual_q = base.filter(Trabajo.contrato_id.is_(None))
    fijo_q = base.filter(Trabajo.contrato_id.isnot(None))

    n_eventual = eventual_q.count()
    n_fijo = fijo_q.count()
    rev_eventual = float(eventual_q.with_entities(func.coalesce(func.sum(Trabajo.monto), 0)).scalar() or 0)
    rev_fijo = float(fijo_q.with_entities(func.coalesce(func.sum(Trabajo.monto), 0)).scalar() or 0)

    # Cancelaciones: sobre lo agendado en el período (realizado o cancelado, con
    # fecha_programada en el rango) — un pendiente todavía no tiene desenlace,
    # no cuenta ni como éxito ni como cancelación.
    programados_q = db.query(Trabajo).filter(
        Trabajo.fecha_programada >= desde,
        Trabajo.fecha_programada <= hasta,
        Trabajo.estado.in_([EstadoTrabajo.realizado, EstadoTrabajo.cancelado]),
    )
    total_programados = programados_q.count()
    cancelados = programados_q.filter(Trabajo.estado == EstadoTrabajo.cancelado).count()

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
        "trabajos_eventuales": n_eventual,
        "trabajos_fijos": n_fijo,
        "facturacion_eventual": rev_eventual,
        "facturacion_fija": rev_fijo,
        "ticket_promedio_eventual": (rev_eventual / n_eventual) if n_eventual else 0,
        "ticket_promedio_fijo": (rev_fijo / n_fijo) if n_fijo else 0,
        "pct_ingresos_fijos": (rev_fijo / revenue * 100) if revenue else 0,
        "trabajos_cancelados": cancelados,
        "trabajos_programados_periodo": total_programados,
        "pct_cancelados": (cancelados / total_programados * 100) if total_programados else 0,
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
