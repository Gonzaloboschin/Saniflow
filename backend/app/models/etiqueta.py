from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

# Tablas puente para las relaciones muchos-a-muchos.
trabajo_etiquetas = Table(
    "trabajo_etiquetas", Base.metadata,
    Column("trabajo_id", Integer, ForeignKey("trabajos.id"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id"), primary_key=True),
)

interaccion_etiquetas = Table(
    "interaccion_etiquetas", Base.metadata,
    Column("interaccion_id", Integer, ForeignKey("interacciones.id"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id"), primary_key=True),
)


class Etiqueta(Base):
    """Etiquetas libres (ej: 'reaparición cucarachas', 'demora técnico',
    'acceso difícil'). Se aplican a trabajos y/o interacciones, y contando
    su frecuencia por cliente se detectan problemas recurrentes."""

    __tablename__ = "etiquetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)

    trabajos = relationship("Trabajo", secondary=trabajo_etiquetas, back_populates="etiquetas")
    interacciones = relationship("Interaccion", secondary=interaccion_etiquetas, back_populates="etiquetas")
