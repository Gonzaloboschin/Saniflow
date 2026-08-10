from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import not_found
from app.schemas.interaccion import InteraccionOut, InteraccionCreate, InteraccionResolver
from app import crud

router = APIRouter(prefix="/interacciones", tags=["interacciones"])


@router.post("", response_model=InteraccionOut, status_code=201)
def crear(data: InteraccionCreate, db: Session = Depends(get_db)):
    return crud.interaccion.create(db, data)


@router.post("/{interaccion_id}/resolver", response_model=InteraccionOut)
def resolver(interaccion_id: int, data: InteraccionResolver, db: Session = Depends(get_db)):
    from app.models.interaccion import Interaccion
    interaccion = db.query(Interaccion).filter(Interaccion.id == interaccion_id).first()
    if not interaccion:
        not_found("Interacción", interaccion_id)
    return crud.interaccion.marcar_resuelto(db, interaccion, data.resolucion)
