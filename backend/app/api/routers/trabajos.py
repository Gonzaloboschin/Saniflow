from datetime import date

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import not_found
from app.models.trabajo import EstadoTrabajo
from app.schemas.trabajo import TrabajoOut, TrabajoCreate, TrabajoUpdate, TrabajoCompletar
from app import crud
from app.services import trabajos_service, notificaciones_service

router = APIRouter(prefix="/trabajos", tags=["trabajos"])


def _a_out(t) -> TrabajoOut:
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


@router.get("", response_model=list[TrabajoOut])
def listar(
    estado: EstadoTrabajo | None = None,
    cliente_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
):
    trabajos = crud.trabajo.list_all(db, estado=estado, cliente_id=cliente_id, desde=desde, hasta=hasta)
    return [_a_out(t) for t in trabajos]


@router.post("", response_model=TrabajoOut, status_code=201)
def crear(data: TrabajoCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    trabajo = crud.trabajo.create(db, data)
    trabajo_completo = crud.trabajo.get(db, trabajo.id)
    notificaciones_service.notificar_nuevo_trabajo_en_segundo_plano(background_tasks, trabajo_completo)
    return _a_out(trabajo_completo)


@router.get("/{trabajo_id}", response_model=TrabajoOut)
def obtener(trabajo_id: int, db: Session = Depends(get_db)):
    trabajo = crud.trabajo.get(db, trabajo_id)
    if not trabajo:
        not_found("Trabajo", trabajo_id)
    return _a_out(trabajo)


@router.patch("/{trabajo_id}", response_model=TrabajoOut)
def actualizar(trabajo_id: int, data: TrabajoUpdate, db: Session = Depends(get_db)):
    trabajo = crud.trabajo.get(db, trabajo_id)
    if not trabajo:
        not_found("Trabajo", trabajo_id)
    trabajo = crud.trabajo.update(db, trabajo, data)
    return _a_out(trabajo)


@router.post("/{trabajo_id}/completar", response_model=dict)
def completar(trabajo_id: int, data: TrabajoCompletar, db: Session = Depends(get_db)):
    trabajo = crud.trabajo.get(db, trabajo_id)
    if not trabajo:
        not_found("Trabajo", trabajo_id)
    cerrado, proximo = trabajos_service.completar_trabajo(db, trabajo, data)
    return {
        "trabajo": _a_out(cerrado),
        "proximo_trabajo_generado": _a_out(proximo) if proximo else None,
    }


@router.post("/{trabajo_id}/cancelar", response_model=TrabajoOut)
def cancelar(trabajo_id: int, db: Session = Depends(get_db)):
    trabajo = crud.trabajo.get(db, trabajo_id)
    if not trabajo:
        not_found("Trabajo", trabajo_id)
    trabajo = crud.trabajo.cancelar(db, trabajo)
    return _a_out(trabajo)
