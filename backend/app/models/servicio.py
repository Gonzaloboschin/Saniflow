from sqlalchemy import Column, Integer, String, Numeric, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Servicio(Base):
    """Catálogo de tipos de servicio (desinsectación, desratización, etc.)."""

    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(300))
    precio_base = Column(Numeric(10, 2), nullable=False, default=0)
    color = Column(String(9), default="#0F5C56")
    activo = Column(Boolean, default=True, nullable=False)

    trabajos = relationship("Trabajo", back_populates="servicio")
    contratos = relationship("Contrato", back_populates="servicio")
