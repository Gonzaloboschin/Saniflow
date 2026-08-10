from pydantic import BaseModel


class Mensaje(BaseModel):
    mensaje: str


class ProblemaRecurrente(BaseModel):
    etiqueta: str
    ocurrencias: int


class ClienteEnRiesgo(BaseModel):
    cliente_id: int
    cliente_nombre: str
    motivo: str
    detalle: str
