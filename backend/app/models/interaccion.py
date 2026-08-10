import enum

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TipoInteraccion(str, enum.Enum):
    reclamo = "reclamo"
    consulta = "consulta"
    llamado = "llamado"
    otro = "otro"


class Interaccion(Base):
    """Bitácora de contacto con el cliente: reclamos, consultas, llamados.
    Es lo que permite responder '¿este cliente reclamó antes?' y, combinado
    con etiquetas, detectar problemas recurrentes."""

    __tablename__ = "interacciones"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    trabajo_id = Column(Integer, ForeignKey("trabajos.id"), nullable=True)
    tipo = Column(Enum(TipoInteraccion), nullable=False, default=TipoInteraccion.consulta, index=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    motivo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    resuelto = Column(Boolean, default=False, nullable=False)
    resolucion = Column(Text)
    registrado_por = Column(String(120))

    cliente = relationship("Cliente", back_populates="interacciones")
    trabajo = relationship("Trabajo")
    etiquetas = relationship("Etiqueta", secondary="interaccion_etiquetas", back_populates="interacciones")
