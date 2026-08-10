from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import not_found
from app.schemas.cliente import ClienteOut, ClienteCreate, ClienteUpdate, ClienteConMetricas
from app.schemas.trabajo import TrabajoOut
from app.schemas.interaccion import InteraccionOut
from app.schemas.common import ProblemaRecurrente
from app import crud
from app.services import clientes_service

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteOut])
def listar_clientes(q: str | None = Query(None, description="Búsqueda por nombre"), db: Session = Depends(get_db)):
    return crud.cliente.list_all(db, q=q)


@router.post("", response_model=ClienteOut, status_code=201)
def crear_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    return crud.cliente.create(db, data)


@router.get("/en-riesgo", response_model=list)
def clientes_en_riesgo(db: Session = Depends(get_db)):
    return clientes_service.clientes_en_riesgo(db)


@router.get("/{cliente_id}", response_model=ClienteConMetricas)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = crud.cliente.get(db, cliente_id)
    if not cliente:
        not_found("Cliente", cliente_id)
    metricas = crud.cliente.metricas(db, cliente_id)
    return ClienteConMetricas(**ClienteOut.model_validate(cliente).model_dump(), **metricas)


@router.patch("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(cliente_id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = crud.cliente.get(db, cliente_id)
    if not cliente:
        not_found("Cliente", cliente_id)
    return crud.cliente.update(db, cliente, data)


@router.get("/{cliente_id}/historial", response_model=list[TrabajoOut])
def historial_trabajos(cliente_id: int, db: Session = Depends(get_db)):
    trabajos = crud.trabajo.list_all(db, cliente_id=cliente_id)
    return [_trabajo_a_out(t) for t in trabajos]


@router.get("/{cliente_id}/interacciones", response_model=list[InteraccionOut])
def interacciones_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return crud.interaccion.list_by_cliente(db, cliente_id)


@router.get("/{cliente_id}/problemas-recurrentes", response_model=list[ProblemaRecurrente])
def problemas_recurrentes(cliente_id: int, db: Session = Depends(get_db)):
    return clientes_service.problemas_recurrentes(db, cliente_id)


def _trabajo_a_out(t) -> TrabajoOut:
    return TrabajoOut(
        **{k: getattr(t, k) for k in [
            "id", "codigo", "cliente_id", "servicio_id", "tecnico_id", "contrato_id",
            "fecha_programada", "hora_programada", "prioridad", "notas", "estado",
            "hora_inicio", "hora_fin", "duracion_min", "monto", "costo",
            "detalle_trabajo", "fecha_realizado", "creado_en",
        ]},
        cliente_nombre=t.cliente.nombre if t.cliente else None,
        servicio_nombre=t.servicio.nombre if t.servicio else None,
        servicio_color=t.servicio.color if t.servicio else None,
        tecnico_nombre=t.tecnico.nombre if t.tecnico else None,
    )
