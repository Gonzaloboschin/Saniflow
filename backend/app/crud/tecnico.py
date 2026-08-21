from sqlalchemy.orm import Session

from app.models.tecnico import Tecnico
from app.schemas.tecnico import TecnicoCreate, TecnicoUpdate


def get(db: Session, tecnico_id: int) -> Tecnico | None:
    return db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()


def list_all(db: Session, solo_activos: bool = False) -> list[Tecnico]:
    query = db.query(Tecnico)
    if solo_activos:
        query = query.filter(Tecnico.activo.is_(True))
    return query.order_by(Tecnico.nombre).all()


def create(db: Session, data: TecnicoCreate) -> Tecnico:
    tecnico = Tecnico(**data.model_dump())
    db.add(tecnico)
    db.commit()
    db.refresh(tecnico)
    return tecnico


def update(db: Session, tecnico: Tecnico, data: TecnicoUpdate) -> Tecnico:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tecnico, field, value)
    db.commit()
    db.refresh(tecnico)
    return tecnico
