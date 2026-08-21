from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import not_found
from app.schemas.tecnico import TecnicoOut, TecnicoCreate, TecnicoUpdate
from app import crud

router = APIRouter(prefix="/tecnicos", tags=["tecnicos"])


@router.get("", response_model=list[TecnicoOut])
def listar(solo_activos: bool = False, db: Session = Depends(get_db)):
    return crud.tecnico.list_all(db, solo_activos=solo_activos)


@router.post("", response_model=TecnicoOut, status_code=201)
def crear(data: TecnicoCreate, db: Session = Depends(get_db)):
    return crud.tecnico.create(db, data)


@router.get("/{tecnico_id}", response_model=TecnicoOut)
def obtener(tecnico_id: int, db: Session = Depends(get_db)):
    tecnico = crud.tecnico.get(db, tecnico_id)
    if not tecnico:
        not_found("Técnico", tecnico_id)
    return tecnico


@router.patch("/{tecnico_id}", response_model=TecnicoOut)
def actualizar(tecnico_id: int, data: TecnicoUpdate, db: Session = Depends(get_db)):
    tecnico = crud.tecnico.get(db, tecnico_id)
    if not tecnico:
        not_found("Técnico", tecnico_id)
    return crud.tecnico.update(db, tecnico, data)
