import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
from fastapi import BackgroundTasks

from app.core.config import settings
from app.models.trabajo import Trabajo, PrioridadTrabajo

logger = logging.getLogger("saniflow.notificaciones")


def _enviar_via_resend(destinatarios: list[str], asunto: str, cuerpo: str) -> bool:
    try:
        respuesta = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={"from": settings.resend_from, "to": destinatarios, "subject": asunto, "text": cuerpo},
            timeout=10,
        )
        respuesta.raise_for_status()
        logger.info("Mail enviado vía Resend a %s (id: %s)", destinatarios, respuesta.json().get("id"))
        return True
    except Exception:
        logger.exception("Error enviando mail vía Resend a %s", destinatarios)
        return False


def _enviar_via_smtp(destinatarios: list[str], asunto: str, cuerpo: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_user}>"
        msg["To"] = ", ".join(destinatarios)
        msg["Subject"] = asunto
        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_user, destinatarios, msg.as_string())
        return True
    except Exception:
        logger.exception("Error enviando mail vía SMTP a %s", destinatarios)
        return False


def enviar_mail(destinatarios: list[str], asunto: str, cuerpo: str) -> bool:
    """Manda un mail de texto plano. Nunca levanta una excepción hacia
    afuera — si falla, lo deja registrado en el log y devuelve False,
    para que nunca tire abajo el resto de la request que lo disparó.

    Prioriza Resend (API con key); si no está configurado, cae a SMTP
    como respaldo; si ninguno está configurado, no hace nada."""
    if not destinatarios:
        return False
    if settings.resend_api_key and settings.resend_from:
        return _enviar_via_resend(destinatarios, asunto, cuerpo)
    if settings.smtp_host and settings.smtp_user and settings.smtp_password:
        return _enviar_via_smtp(destinatarios, asunto, cuerpo)
    logger.info("Sin proveedor de mail configurado (ni Resend ni SMTP) — se omite el envío a %s.", destinatarios)
    return False


def _construir_nuevo_trabajo(trabajo: Trabajo) -> tuple[list[str], str, str]:
    """Arma destinatarios/asunto/cuerpo para el aviso de un trabajo recién
    cargado. No hace I/O — solo lee de los objetos ya cargados en memoria
    (`trabajo.cliente`, `trabajo.servicio`, `trabajo.tecnico`), así se
    puede llamar de forma segura antes de que se cierre la sesión de la
    base de datos."""
    cliente = trabajo.cliente
    servicio = trabajo.servicio
    tecnico = trabajo.tecnico

    prioridad_txt = "Urgente" if trabajo.prioridad == PrioridadTrabajo.urgente else "Normal"
    tecnico_txt = tecnico.nombre if tecnico else "Sin asignar"

    asunto = f"Nuevo trabajo — {cliente.nombre} — {trabajo.fecha_programada.strftime('%d/%m/%Y')}"
    cuerpo = (
        "Se cargó un trabajo nuevo en SaniFlow.\n\n"
        f"Cliente: {cliente.nombre}\n"
        f"Dirección: {cliente.direccion or '-'}\n"
        f"Teléfono: {cliente.telefono or '-'}\n"
        f"Servicio: {servicio.nombre}\n"
        f"Fecha: {trabajo.fecha_programada.strftime('%d/%m/%Y')}\n"
        f"Hora: {trabajo.hora_programada.strftime('%H:%M')}\n"
        f"Técnico asignado: {tecnico_txt}\n"
        f"Prioridad: {prioridad_txt}\n"
        f"Notas: {trabajo.notas or '-'}\n\n"
        "— SaniFlow"
    )

    destinatarios = list(settings.admin_emails_list)
    if tecnico and tecnico.email:
        destinatarios.append(tecnico.email)

    return destinatarios, asunto, cuerpo


def notificar_nuevo_trabajo_en_segundo_plano(background_tasks: BackgroundTasks, trabajo: Trabajo) -> None:
    """Se llama desde el router justo después de crear el trabajo, con la
    sesión de la base todavía abierta. Arma el mail ya mismo (rápido, sin
    red) y deja el envío real (que sí puede tardar) para después de haber
    respondido al usuario — así cargar un trabajo no se siente más lento
    por esperar a que salga el mail."""
    destinatarios, asunto, cuerpo = _construir_nuevo_trabajo(trabajo)
    if destinatarios:
        background_tasks.add_task(enviar_mail, destinatarios, asunto, cuerpo)
