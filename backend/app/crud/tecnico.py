from sqlalchemy.orm import Session

from app.models.tecnico import Tecnico
from app.schemas.tecnico import TecnicoCreate


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
