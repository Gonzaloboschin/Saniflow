from sqlalchemy.orm import Session

from app.models.contrato import Contrato
from app.schemas.contrato import ContratoCreate, ContratoUpdate


def get(db: Session, contrato_id: int) -> Contrato | None:
    return db.query(Contrato).filter(Contrato.id == contrato_id).first()


def list_by_cliente(db: Session, cliente_id: int) -> list[Contrato]:
    return (
        db.query(Contrato)
        .filter(Contrato.cliente_id == cliente_id)
        .order_by(Contrato.fecha_inicio.desc())
        .all()
    )


def create(db: Session, data: ContratoCreate) -> Contrato:
    contrato = Contrato(**data.model_dump())
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return contrato


def update(db: Session, contrato: Contrato, data: ContratoUpdate) -> Contrato:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contrato, field, value)
    db.commit()
    db.refresh(contrato)
    return contrato
