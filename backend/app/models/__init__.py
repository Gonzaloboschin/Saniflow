# Importamos todos los modelos acá para que Alembic (autogenerate) y
# SQLAlchemy los detecten al construir el metadata.
from app.models.cliente import Cliente, TipoCliente, EstadoCliente  # noqa
from app.models.servicio import Servicio  # noqa
from app.models.tecnico import Tecnico  # noqa
from app.models.contrato import Contrato, FrecuenciaContrato, FRECUENCIA_A_DIAS  # noqa
from app.models.trabajo import Trabajo, EstadoTrabajo, PrioridadTrabajo  # noqa
from app.models.interaccion import Interaccion, TipoInteraccion  # noqa
from app.models.etiqueta import Etiqueta, trabajo_etiquetas, interaccion_etiquetas  # noqa
