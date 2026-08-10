import enum

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Date, Time, Numeric, Enum, Text, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class EstadoTrabajo(str, enum.Enum):
    pendiente = "pendiente"
    realizado = "realizado"
    cancelado = "cancelado"


class PrioridadTrabajo(str, enum.Enum):
    normal = "normal"
    urgente = "urgente"


class Trabajo(Base):
    """Una visita/servicio, programado o ya realizado. Es la unidad
    operativa del sistema: nace pendiente y se cierra con los datos
    reales (monto, costo, duración, detalle)."""

    __tablename__ = "trabajos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id"), nullable=True)
    contrato_id = Column(Integer, ForeignKey("contratos.id"), nullable=True)

    fecha_programada = Column(Date, nullable=False, index=True)
    hora_programada = Column(Time, nullable=False)
    prioridad = Column(Enum(PrioridadTrabajo), default=PrioridadTrabajo.normal, nullable=False)
    estado = Column(Enum(EstadoTrabajo), default=EstadoTrabajo.pendiente, nullable=False, index=True)
    notas = Column(Text)

    # Se completan al cerrar el trabajo:
    hora_inicio = Column(Time, nullable=True)
    hora_fin = Column(Time, nullable=True)
    duracion_min = Column(Integer, nullable=True)
    monto = Column(Numeric(10, 2), nullable=True)
    costo = Column(Numeric(10, 2), nullable=True)
    detalle_trabajo = Column(Text, nullable=True)
    fecha_realizado = Column(Date, nullable=True, index=True)

    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    cliente = relationship("Cliente", back_populates="trabajos")
    servicio = relationship("Servicio", back_populates="trabajos")
    tecnico = relationship("Tecnico", back_populates="trabajos")
    contrato = relationship("Contrato", back_populates="trabajos")
    etiquetas = relationship("Etiqueta", secondary="trabajo_etiquetas", back_populates="trabajos")
