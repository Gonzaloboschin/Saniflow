from sqlalchemy.orm import Session

from app.models.servicio import Servicio
from app.schemas.servicio import ServicioCreate, ServicioUpdate


def get(db: Session, servicio_id: int) -> Servicio | None:
    return db.query(Servicio).filter(Servicio.id == servicio_id).first()


def list_all(db: Session, solo_activos: bool = False) -> list[Servicio]:
    query = db.query(Servicio)
    if solo_activos:
        query = query.filter(Servicio.activo.is_(True))
    return query.order_by(Servicio.nombre).all()


def create(db: Session, data: ServicioCreate) -> Servicio:
    servicio = Servicio(**data.model_dump())
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


def update(db: Session, servicio: Servicio, data: ServicioUpdate) -> Servicio:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(servicio, field, value)
    db.commit()
    db.refresh(servicio)
    return servicio
