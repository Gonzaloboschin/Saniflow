from datetime import date

from app.core.config import settings


def _crear_servicio(client):
    r = client.post("/servicios", json={"nombre": "Desinsectación", "precio_base": 15000})
    return r.json()["id"]


def _crear_cliente(client, nombre="Cliente de prueba"):
    r = client.post("/clientes", json={"nombre": nombre})
    return r.json()["id"]


def test_sin_ningun_proveedor_configurado_no_manda_nada_y_no_rompe(client, monkeypatch):
    """Si no hay ni Resend ni SMTP configurados, crear un trabajo tiene
    que funcionar igual — la notificación se omite en silencio."""
    monkeypatch.setattr(settings, "resend_api_key", "")
    monkeypatch.setattr(settings, "resend_from", "")
    monkeypatch.setattr(settings, "smtp_host", "")
    monkeypatch.setattr(settings, "smtp_user", "")
    monkeypatch.setattr(settings, "smtp_password", "")

    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client)

    r = client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id,
        "fecha_programada": str(date.today()), "hora_programada": "09:00:00",
    })
    assert r.status_code == 201


def test_crear_trabajo_notifica_a_los_administradores(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_emails", "boschingon@gmail.com,boschinch@gmail.com")

    llamadas = []

    def fake_enviar_mail(destinatarios, asunto, cuerpo):
        llamadas.append({"destinatarios": destinatarios, "asunto": asunto, "cuerpo": cuerpo})
        return True

    monkeypatch.setattr("app.services.notificaciones_service.enviar_mail", fake_enviar_mail)

    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client, "Farmacia de Prueba")

    r = client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id,
        "fecha_programada": str(date.today()), "hora_programada": "10:30:00",
        "notas": "Cliente pidió que avisen antes de ir",
    })
    assert r.status_code == 201

    assert len(llamadas) == 1
    llamada = llamadas[0]
    assert "boschingon@gmail.com" in llamada["destinatarios"]
    assert "boschinch@gmail.com" in llamada["destinatarios"]
    assert "Farmacia de Prueba" in llamada["asunto"]
    assert "Cliente pidió que avisen antes de ir" in llamada["cuerpo"]


def test_notifica_tambien_al_tecnico_si_tiene_mail_cargado(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_emails", "boschingon@gmail.com")

    llamadas = []
    monkeypatch.setattr(
        "app.services.notificaciones_service.enviar_mail",
        lambda destinatarios, asunto, cuerpo: llamadas.append(destinatarios) or True,
    )

    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client)
    r = client.post("/tecnicos", json={"nombre": "Daniel Berón", "email": "daniel@example.com"})
    tecnico_id = r.json()["id"]

    client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id, "tecnico_id": tecnico_id,
        "fecha_programada": str(date.today()), "hora_programada": "09:00:00",
    })

    assert len(llamadas) == 1
    assert "daniel@example.com" in llamadas[0]
    assert "boschingon@gmail.com" in llamadas[0]


def test_no_notifica_al_tecnico_sin_mail_cargado(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_emails", "boschingon@gmail.com")

    llamadas = []
    monkeypatch.setattr(
        "app.services.notificaciones_service.enviar_mail",
        lambda destinatarios, asunto, cuerpo: llamadas.append(destinatarios) or True,
    )

    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client)
    r = client.post("/tecnicos", json={"nombre": "Daniel Berón"})  # sin email
    tecnico_id = r.json()["id"]

    client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id, "tecnico_id": tecnico_id,
        "fecha_programada": str(date.today()), "hora_programada": "09:00:00",
    })

    assert len(llamadas) == 1
    assert llamadas[0] == ["boschingon@gmail.com"]


def test_enviar_mail_usa_resend_cuando_esta_configurado(monkeypatch):
    """No conecta a ningún servidor real — reemplaza httpx.post por un
    doble de prueba y confirma que llama a la API de Resend con los
    parámetros correctos."""
    from app.services.notificaciones_service import enviar_mail
    import app.services.notificaciones_service as mod

    monkeypatch.setattr(settings, "resend_api_key", "re_test_123")
    monkeypatch.setattr(settings, "resend_from", "SaniFlow <administracion@sanrafaeldesinfecciones.com>")

    llamadas = {}

    class FakeRespuesta:
        def raise_for_status(self):
            pass

        def json(self):
            return {"id": "resend-id-de-prueba"}

    def fake_post(url, headers=None, json=None, timeout=None):
        llamadas["url"] = url
        llamadas["headers"] = headers
        llamadas["json"] = json
        return FakeRespuesta()

    monkeypatch.setattr(mod.httpx, "post", fake_post)

    resultado = enviar_mail(["destino@example.com"], "Asunto de prueba", "Cuerpo de prueba")

    assert resultado is True
    assert llamadas["url"] == "https://api.resend.com/emails"
    assert llamadas["headers"]["Authorization"] == "Bearer re_test_123"
    assert llamadas["json"]["from"] == "SaniFlow <administracion@sanrafaeldesinfecciones.com>"
    assert llamadas["json"]["to"] == ["destino@example.com"]
    assert llamadas["json"]["subject"] == "Asunto de prueba"


def test_enviar_mail_cae_a_smtp_si_no_hay_resend_configurado(monkeypatch):
    """Si Resend no está configurado pero SMTP sí, usa SMTP como
    respaldo — sin conectar a ningún servidor real."""
    from app.services.notificaciones_service import enviar_mail
    import app.services.notificaciones_service as mod

    monkeypatch.setattr(settings, "resend_api_key", "")
    monkeypatch.setattr(settings, "resend_from", "")
    monkeypatch.setattr(settings, "smtp_host", "smtp.ejemplo.com")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_user", "user@ejemplo.com")
    monkeypatch.setattr(settings, "smtp_password", "clave")

    llamadas = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=10):
            llamadas["host"] = host

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def starttls(self):
            pass

        def login(self, user, password):
            llamadas["login"] = (user, password)

        def sendmail(self, from_addr, to_addrs, msg):
            llamadas["sendmail"] = True

    monkeypatch.setattr(mod.smtplib, "SMTP", FakeSMTP)

    resultado = enviar_mail(["destino@example.com"], "Asunto", "Cuerpo")

    assert resultado is True
    assert llamadas["host"] == "smtp.ejemplo.com"
    assert llamadas["sendmail"] is True


def test_crud_tecnicos_completo(client):
    r = client.post("/tecnicos", json={"nombre": "Lucas Peralta", "telefono": "260123", "email": "lucas@example.com"})
    assert r.status_code == 201
    tecnico_id = r.json()["id"]
    assert r.json()["activo"] is True

    r = client.get(f"/tecnicos/{tecnico_id}")
    assert r.status_code == 200
    assert r.json()["email"] == "lucas@example.com"

    r = client.patch(f"/tecnicos/{tecnico_id}", json={"activo": False})
    assert r.status_code == 200
    assert r.json()["activo"] is False

    r = client.get("/tecnicos", params={"solo_activos": True})
    assert tecnico_id not in [t["id"] for t in r.json()]

    r = client.get("/tecnicos", params={"solo_activos": False})
    assert tecnico_id in [t["id"] for t in r.json()]
