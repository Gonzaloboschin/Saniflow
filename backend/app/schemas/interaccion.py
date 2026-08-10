from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.interaccion import TipoInteraccion


class InteraccionBase(BaseModel):
    cliente_id: int
    trabajo_id: int | None = None
    tipo: TipoInteraccion
    motivo: str
    descripcion: str | None = None
    registrado_por: str | None = None
    etiquetas: list[str] = []


class InteraccionCreate(InteraccionBase):
    pass


class InteraccionResolver(BaseModel):
    resolucion: str


class InteraccionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    trabajo_id: int | None
    tipo: TipoInteraccion
    fecha: datetime
    motivo: str
    descripcion: str | None
    resuelto: bool
    resolucion: str | None
    registrado_por: str | None
