from datetime import date, time, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.models.trabajo import EstadoTrabajo, PrioridadTrabajo


class TrabajoBase(BaseModel):
    cliente_id: int
    servicio_id: int
    tecnico_id: int | None = None
    contrato_id: int | None = None
    fecha_programada: date
    hora_programada: time
    prioridad: PrioridadTrabajo = PrioridadTrabajo.normal
    notas: str | None = None


class TrabajoCreate(TrabajoBase):
    pass


class TrabajoUpdate(BaseModel):
    tecnico_id: int | None = None
    fecha_programada: date | None = None
    hora_programada: time | None = None
    prioridad: PrioridadTrabajo | None = None
    notas: str | None = None


class TrabajoCompletar(BaseModel):
    """Payload para cerrar un trabajo pendiente."""
    hora_inicio: time
    hora_fin: time
    monto: Decimal
    costo: Decimal = Decimal("0")
    detalle_trabajo: str | None = None
    etiquetas: list[str] = []  # nombres de etiquetas, ej: ["reaparición plaga"]


class TrabajoOut(TrabajoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    estado: EstadoTrabajo
    hora_inicio: time | None = None
    hora_fin: time | None = None
    duracion_min: int | None = None
    monto: Decimal | None = None
    costo: Decimal | None = None
    detalle_trabajo: str | None = None
    fecha_realizado: date | None = None
    creado_en: datetime

    # Datos "planos" de las relaciones más usados en listas, para no forzar
    # otro request desde el frontend.
    cliente_nombre: str | None = None
    servicio_nombre: str | None = None
    servicio_color: str | None = None
    tecnico_nombre: str | None = None
