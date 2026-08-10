from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tecnico import TecnicoOut, TecnicoCreate
from app import crud

router = APIRouter(prefix="/tecnicos", tags=["tecnicos"])


@router.get("", response_model=list[TecnicoOut])
def listar(solo_activos: bool = False, db: Session = Depends(get_db)):
    return crud.tecnico.list_all(db, solo_activos=solo_activos)


@router.post("", response_model=TecnicoOut, status_code=201)
def crear(data: TecnicoCreate, db: Session = Depends(get_db)):
    return crud.tecnico.create(db, data)
