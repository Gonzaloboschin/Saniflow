from datetime import date

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.trabajo import Trabajo, EstadoTrabajo
from app.models.cliente import Cliente
from app.models.servicio import Servicio
from app.models.tecnico import Tecnico
from app.schemas.trabajo import TrabajoCreate, TrabajoUpdate


def _siguiente_codigo(db: Session) -> str:
    total = db.query(Trabajo).count()
    return f"T-{total + 1:05d}"


def get(db: Session, trabajo_id: int) -> Trabajo | None:
    return (
        db.query(Trabajo)
        .options(joinedload(Trabajo.cliente), joinedload(Trabajo.servicio), joinedload(Trabajo.tecnico))
        .filter(Trabajo.id == trabajo_id)
        .first()
    )


def list_all(
    db: Session,
    estado: EstadoTrabajo | None = None,
    cliente_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    skip: int = 0,
    limit: int = 500,
) -> list[Trabajo]:
    query = db.query(Trabajo).options(
        joinedload(Trabajo.cliente), joinedload(Trabajo.servicio), joinedload(Trabajo.tecnico)
    )
    filtros = []
    if estado:
        filtros.append(Trabajo.estado == estado)
    if cliente_id:
        filtros.append(Trabajo.cliente_id == cliente_id)
    if desde:
        filtros.append(Trabajo.fecha_programada >= desde)
    if hasta:
        filtros.append(Trabajo.fecha_programada <= hasta)
    if filtros:
        query = query.filter(and_(*filtros))

    orden = (
        (Trabajo.fecha_programada, Trabajo.hora_programada)
        if estado == EstadoTrabajo.pendiente
        else (Trabajo.fecha_realizado.desc(),)
    )
    return query.order_by(*orden).offset(skip).limit(limit).all()


def create(db: Session, data: TrabajoCreate) -> Trabajo:
    trabajo = Trabajo(**data.model_dump(), codigo=_siguiente_codigo(db), estado=EstadoTrabajo.pendiente)
    db.add(trabajo)
    db.commit()
    db.refresh(trabajo)
    return trabajo


def update(db: Session, trabajo: Trabajo, data: TrabajoUpdate) -> Trabajo:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(trabajo, field, value)
    db.commit()
    db.refresh(trabajo)
    return trabajo


def cancelar(db: Session, trabajo: Trabajo) -> Trabajo:
    trabajo.estado = EstadoTrabajo.cancelado
    db.commit()
    db.refresh(trabajo)
    return trabajo
