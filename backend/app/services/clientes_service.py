from datetime import date, timedelta
from collections import Counter

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.trabajo import Trabajo, EstadoTrabajo
from app.models.interaccion import Interaccion, TipoInteraccion
from app.models.contrato import Contrato, FRECUENCIA_A_DIAS
from app.schemas.common import ProblemaRecurrente, ClienteEnRiesgo


def problemas_recurrentes(db: Session, cliente_id: int, minimo_ocurrencias: int = 2) -> list[ProblemaRecurrente]:
    """Cuenta etiquetas usadas en los trabajos e interacciones de un cliente.
    Una etiqueta que aparece 2+ veces se considera un problema recurrente
    (ej: 'reaparición cucarachas' en varias visitas seguidas)."""
    trabajos = db.query(Trabajo).filter(Trabajo.cliente_id == cliente_id).all()
    interacciones = db.query(Interaccion).filter(Interaccion.cliente_id == cliente_id).all()

    contador = Counter()
    for t in trabajos:
        for e in t.etiquetas:
            contador[e.nombre] += 1
    for i in interacciones:
        for e in i.etiquetas:
            contador[e.nombre] += 1

    return [
        ProblemaRecurrente(etiqueta=nombre, ocurrencias=n)
        for nombre, n in contador.most_common()
        if n >= minimo_ocurrencias
    ]


def clientes_en_riesgo(db: Session, ventana_dias_reclamos: int = 90, reclamos_minimos: int = 2) -> list[ClienteEnRiesgo]:
    """Heurística simple de riesgo, pensada para ampliarse con más señales:
      1) 2+ reclamos en los últimos N días.
      2) Contrato activo cuyo próximo servicio ya venció y no hay nada agendado.
    """
    resultado: list[ClienteEnRiesgo] = []
    limite = date.today() - timedelta(days=ventana_dias_reclamos)

    # Señal 1: reclamos recientes
    clientes = db.query(Cliente).all()
    for cliente in clientes:
        reclamos_recientes = [
            i for i in cliente.interacciones
            if i.tipo == TipoInteraccion.reclamo and i.fecha.date() >= limite
        ]
        if len(reclamos_recientes) >= reclamos_minimos:
            resultado.append(ClienteEnRiesgo(
                cliente_id=cliente.id,
                cliente_nombre=cliente.nombre,
                motivo="reclamos_frecuentes",
                detalle=f"{len(reclamos_recientes)} reclamos en los últimos {ventana_dias_reclamos} días",
            ))

    # Señal 2: contrato vencido sin próxima visita agendada
    contratos_activos = db.query(Contrato).filter(Contrato.activo.is_(True)).all()
    for contrato in contratos_activos:
        dias = FRECUENCIA_A_DIAS.get(contrato.frecuencia)
        if not dias:
            continue
        ultimo_realizado = max(
            (t.fecha_realizado for t in contrato.trabajos if t.estado == EstadoTrabajo.realizado and t.fecha_realizado),
            default=None,
        )
        hay_pendiente = any(t.estado == EstadoTrabajo.pendiente for t in contrato.trabajos)
        if ultimo_realizado and not hay_pendiente:
            vencimiento = ultimo_realizado + timedelta(days=dias)
            if vencimiento < date.today():
                resultado.append(ClienteEnRiesgo(
                    cliente_id=contrato.cliente_id,
                    cliente_nombre=contrato.cliente.nombre,
                    motivo="contrato_vencido_sin_agenda",
                    detalle=f"Última visita {ultimo_realizado.isoformat()}, "
                            f"correspondía repetir el {vencimiento.isoformat()} y no hay nada agendado",
                ))

    return resultado
