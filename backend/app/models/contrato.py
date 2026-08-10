import enum

from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Boolean, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class FrecuenciaContrato(str, enum.Enum):
    semanal = "semanal"
    quincenal = "quincenal"
    mensual = "mensual"
    trimestral = "trimestral"
    semestral = "semestral"
    anual = "anual"
    a_demanda = "a_demanda"


# Mapeo de frecuencia -> cada cuántos días se debe generar el próximo trabajo.
# "a_demanda" es None porque no se auto-agenda: el cliente llama cuando necesita.
FRECUENCIA_A_DIAS = {
    FrecuenciaContrato.semanal: 7,
    FrecuenciaContrato.quincenal: 15,
    FrecuenciaContrato.mensual: 30,
    FrecuenciaContrato.trimestral: 90,
    FrecuenciaContrato.semestral: 180,
    FrecuenciaContrato.anual: 365,
    FrecuenciaContrato.a_demanda: None,
}


class Contrato(Base):
    """Acuerdo de servicio recurrente con un cliente. Guardamos el historial
    completo (no se borran, se dan de baja con fecha_fin) para poder ver
    si un cliente cambió de frecuencia con el tiempo."""

    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    frecuencia = Column(Enum(FrecuenciaContrato), nullable=False, default=FrecuenciaContrato.mensual)
    precio_acordado = Column(Numeric(10, 2))
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    cliente = relationship("Cliente", back_populates="contratos")
    servicio = relationship("Servicio", back_populates="contratos")
    trabajos = relationship("Trabajo", back_populates="contrato")
