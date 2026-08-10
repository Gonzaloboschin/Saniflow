from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.trabajo import Trabajo, EstadoTrabajo
from app.models.interaccion import Interaccion, TipoInteraccion
from app.schemas.cliente import ClienteCreate, ClienteUpdate


def get(db: Session, cliente_id: int) -> Cliente | None:
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()


def list_all(db: Session, q: str | None = None, skip: int = 0, limit: int = 200) -> list[Cliente]:
    query = db.query(Cliente)
    if q:
        query = query.filter(Cliente.nombre.ilike(f"%{q}%"))
    return query.order_by(Cliente.nombre).offset(skip).limit(limit).all()


def create(db: Session, data: ClienteCreate) -> Cliente:
    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def update(db: Session, cliente: Cliente, data: ClienteUpdate) -> Cliente:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)
    db.commit()
    db.refresh(cliente)
    return cliente


def metricas(db: Session, cliente_id: int) -> dict:
    """Números de resumen para la ficha de cliente."""
    total_trabajos = (
        db.query(func.count(Trabajo.id))
        .filter(Trabajo.cliente_id == cliente_id, Trabajo.estado == EstadoTrabajo.realizado)
        .scalar() or 0
    )
    total_facturado = (
        db.query(func.coalesce(func.sum(Trabajo.monto), 0))
        .filter(Trabajo.cliente_id == cliente_id, Trabajo.estado == EstadoTrabajo.realizado)
        .scalar() or 0
    )
    total_reclamos = (
        db.query(func.count(Interaccion.id))
        .filter(Interaccion.cliente_id == cliente_id, Interaccion.tipo == TipoInteraccion.reclamo)
        .scalar() or 0
    )
    ultimo_trabajo = (
        db.query(func.max(Trabajo.fecha_realizado))
        .filter(Trabajo.cliente_id == cliente_id, Trabajo.estado == EstadoTrabajo.realizado)
        .scalar()
    )
    return {
        "total_trabajos_realizados": total_trabajos,
        "total_facturado": float(total_facturado),
        "total_reclamos": total_reclamos,
        "ultimo_trabajo": ultimo_trabajo,
    }
