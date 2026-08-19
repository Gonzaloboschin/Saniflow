from typing import Literal
from pydantic import BaseModel


class FilaImportacion(BaseModel):
    """Una fila tal como viene de la planilla — todo texto crudo, sin
    interpretar todavía. El mismo shape se usa para mandar la vista previa
    al frontend y para que el frontend la devuelva sin tocar al confirmar."""
    nombre: str = ""
    tipo: str = ""
    telefono: str = ""
    email: str = ""
    direccion: str = ""
    localidad: str = ""
    notas: str = ""
    servicio: str = ""
    frecuencia: str = ""
    precio_acordado: str = ""


class FilaImportacionPreview(BaseModel):
    fila: int
    datos: FilaImportacion
    estado: Literal["ok", "advertencia", "error", "duplicado"]
    mensajes: list[str]
    # Campos solo para mostrar en la vista previa (no se vuelven a mandar al confirmar).
    tipo_resuelto: str
    es_fijo: bool
    servicio_resuelto: str | None = None


class ResumenImportacion(BaseModel):
    creados: int
    contratos_creados: int
    omitidos: int
    detalles: list[FilaImportacionPreview]
