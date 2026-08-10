import enum

from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TipoCliente(str, enum.Enum):
    particular = "particular"
    comercio = "comercio"
    industria = "industria"


class EstadoCliente(str, enum.Enum):
    activo = "activo"
    en_riesgo = "en_riesgo"
    inactivo = "inactivo"


class Cliente(Base):
    """Ficha de cliente: es el eje del CRM. Todo (trabajos, contratos,
    reclamos) cuelga de acá para poder armar el historial completo."""

    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    tipo = Column(Enum(TipoCliente), default=TipoCliente.particular, nullable=False)
    telefono = Column(String(50))
    email = Column(String(200))
    direccion = Column(String(300))
    localidad = Column(String(120))
    estado = Column(Enum(EstadoCliente), default=EstadoCliente.activo, nullable=False, index=True)
    notas = Column(Text)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    trabajos = relationship("Trabajo", back_populates="cliente", order_by="Trabajo.fecha_programada.desc()")
    contratos = relationship("Contrato", back_populates="cliente", order_by="Contrato.fecha_inicio.desc()")
    interacciones = relationship("Interaccion", back_populates="cliente", order_by="Interaccion.fecha.desc()")
