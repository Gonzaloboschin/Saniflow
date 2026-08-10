from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.cliente import TipoCliente, EstadoCliente


class ClienteBase(BaseModel):
    nombre: str
    tipo: TipoCliente = TipoCliente.particular
    telefono: str | None = None
    email: str | None = None
    direccion: str | None = None
    localidad: str | None = None
    notas: str | None = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: str | None = None
    tipo: TipoCliente | None = None
    telefono: str | None = None
    email: str | None = None
    direccion: str | None = None
    localidad: str | None = None
    estado: EstadoCliente | None = None
    notas: str | None = None


class ClienteOut(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    estado: EstadoCliente
    creado_en: datetime


class ClienteConMetricas(ClienteOut):
    """Ficha de cliente enriquecida para la vista de detalle."""
    total_trabajos_realizados: int = 0
    total_facturado: float = 0
    total_reclamos: int = 0
    ultimo_trabajo: datetime | None = None
