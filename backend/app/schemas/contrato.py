from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.models.contrato import FrecuenciaContrato


class ContratoBase(BaseModel):
    cliente_id: int
    servicio_id: int
    frecuencia: FrecuenciaContrato
    precio_acordado: Decimal | None = None
    fecha_inicio: date
    fecha_fin: date | None = None


class ContratoCreate(ContratoBase):
    pass


class ContratoUpdate(BaseModel):
    frecuencia: FrecuenciaContrato | None = None
    precio_acordado: Decimal | None = None
    fecha_fin: date | None = None
    activo: bool | None = None


class ContratoOut(ContratoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
