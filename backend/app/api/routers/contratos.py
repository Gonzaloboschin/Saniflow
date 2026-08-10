from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import not_found
from app.schemas.contrato import ContratoOut, ContratoCreate, ContratoUpdate
from app import crud

router = APIRouter(prefix="/contratos", tags=["contratos"])


@router.post("", response_model=ContratoOut, status_code=201)
def crear(data: ContratoCreate, db: Session = Depends(get_db)):
    return crud.contrato.create(db, data)


@router.get("/cliente/{cliente_id}", response_model=list[ContratoOut])
def listar_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return crud.contrato.list_by_cliente(db, cliente_id)


@router.patch("/{contrato_id}", response_model=ContratoOut)
def actualizar(contrato_id: int, data: ContratoUpdate, db: Session = Depends(get_db)):
    contrato = crud.contrato.get(db, contrato_id)
    if not contrato:
        not_found("Contrato", contrato_id)
    return crud.contrato.update(db, contrato, data)
