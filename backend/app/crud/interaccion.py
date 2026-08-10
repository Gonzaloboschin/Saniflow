from sqlalchemy.orm import Session, joinedload

from app.models.interaccion import Interaccion
from app.schemas.interaccion import InteraccionCreate
from app.crud.etiqueta import get_or_create_many


def list_by_cliente(db: Session, cliente_id: int) -> list[Interaccion]:
    return (
        db.query(Interaccion)
        .options(joinedload(Interaccion.etiquetas))
        .filter(Interaccion.cliente_id == cliente_id)
        .order_by(Interaccion.fecha.desc())
        .all()
    )


def create(db: Session, data: InteraccionCreate) -> Interaccion:
    payload = data.model_dump(exclude={"etiquetas"})
    interaccion = Interaccion(**payload)
    interaccion.etiquetas = get_or_create_many(db, data.etiquetas)
    db.add(interaccion)
    db.commit()
    db.refresh(interaccion)
    return interaccion


def marcar_resuelto(db: Session, interaccion: Interaccion, resolucion: str) -> Interaccion:
    interaccion.resuelto = True
    interaccion.resolucion = resolucion
    db.commit()
    db.refresh(interaccion)
    return interaccion
