from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import not_found
from app.schemas.servicio import ServicioOut, ServicioCreate, ServicioUpdate
from app import crud

router = APIRouter(prefix="/servicios", tags=["servicios"])


@router.get("", response_model=list[ServicioOut])
def listar(solo_activos: bool = False, db: Session = Depends(get_db)):
    return crud.servicio.list_all(db, solo_activos=solo_activos)


@router.post("", response_model=ServicioOut, status_code=201)
def crear(data: ServicioCreate, db: Session = Depends(get_db)):
    return crud.servicio.create(db, data)


@router.patch("/{servicio_id}", response_model=ServicioOut)
def actualizar(servicio_id: int, data: ServicioUpdate, db: Session = Depends(get_db)):
    servicio = crud.servicio.get(db, servicio_id)
    if not servicio:
        not_found("Servicio", servicio_id)
    return crud.servicio.update(db, servicio, data)
