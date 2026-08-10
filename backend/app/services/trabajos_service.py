from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.trabajo import Trabajo, EstadoTrabajo
from app.models.contrato import FRECUENCIA_A_DIAS
from app.schemas.trabajo import TrabajoCompletar
from app.crud.etiqueta import get_or_create_many
from app.crud import trabajo as crud_trabajo


def _minutos_entre(hi, hf) -> int:
    dt1 = datetime.combine(date.min, hi)
    dt2 = datetime.combine(date.min, hf)
    return max(0, int((dt2 - dt1).total_seconds() // 60))


def completar_trabajo(db: Session, trabajo: Trabajo, datos: TrabajoCompletar) -> tuple[Trabajo, Trabajo | None]:
    """Cierra un trabajo pendiente con los datos reales del servicio y,
    si viene de un contrato activo con frecuencia definida, genera
    automáticamente el próximo trabajo pendiente.

    Devuelve (trabajo_cerrado, proximo_trabajo_o_None).
    """
    trabajo.estado = EstadoTrabajo.realizado
    trabajo.hora_inicio = datos.hora_inicio
    trabajo.hora_fin = datos.hora_fin
    trabajo.duracion_min = _minutos_entre(datos.hora_inicio, datos.hora_fin)
    trabajo.monto = datos.monto
    trabajo.costo = datos.costo
    trabajo.detalle_trabajo = datos.detalle_trabajo
    trabajo.fecha_realizado = date.today()
    trabajo.etiquetas = get_or_create_many(db, datos.etiquetas)

    db.add(trabajo)
    db.commit()
    db.refresh(trabajo)

    proximo = None
    if trabajo.contrato and trabajo.contrato.activo:
        dias = FRECUENCIA_A_DIAS.get(trabajo.contrato.frecuencia)
        contrato_vigente = not trabajo.contrato.fecha_fin or trabajo.contrato.fecha_fin >= date.today()
        if dias and contrato_vigente:
            proximo = Trabajo(
                codigo=crud_trabajo._siguiente_codigo(db),
                cliente_id=trabajo.cliente_id,
                servicio_id=trabajo.servicio_id,
                tecnico_id=trabajo.tecnico_id,
                contrato_id=trabajo.contrato_id,
                fecha_programada=date.today() + timedelta(days=dias),
                hora_programada=trabajo.hora_programada,
                estado=EstadoTrabajo.pendiente,
            )
            db.add(proximo)
            db.commit()
            db.refresh(proximo)

    return trabajo, proximo
