from datetime import date, timedelta


def _crear_servicio(client):
    r = client.post("/servicios", json={"nombre": "Desinsectación", "precio_base": 15000})
    return r.json()["id"]


def _crear_cliente(client, nombre="Cliente de prueba"):
    r = client.post("/clientes", json={"nombre": nombre})
    return r.json()["id"]


def _completar(client, trabajo_id, monto):
    return client.post(f"/trabajos/{trabajo_id}/completar", json={
        "hora_inicio": "09:00:00", "hora_fin": "09:30:00", "monto": monto, "costo": monto * 0.3,
    })


def test_kpis_distingue_eventuales_de_fijos(client):
    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client)

    # Un contrato activo para poder crear un trabajo "fijo"
    r = client.post("/contratos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id, "frecuencia": "mensual",
        "fecha_inicio": str(date.today() - timedelta(days=10)),
    })
    contrato_id = r.json()["id"]

    # Un trabajo eventual (sin contrato) de $10.000
    r = client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id,
        "fecha_programada": str(date.today()), "hora_programada": "09:00:00",
    })
    _completar(client, r.json()["id"], 10000)

    # Un trabajo fijo (con contrato) de $20.000
    r = client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id, "contrato_id": contrato_id,
        "fecha_programada": str(date.today()), "hora_programada": "10:00:00",
    })
    _completar(client, r.json()["id"], 20000)

    kpis = client.get("/dashboard/kpis", params={"periodo": "mes"}).json()

    assert kpis["trabajos_eventuales"] == 1
    assert kpis["trabajos_fijos"] == 1
    assert kpis["facturacion_eventual"] == 10000
    assert kpis["facturacion_fija"] == 20000
    assert kpis["ticket_promedio_eventual"] == 10000
    assert kpis["ticket_promedio_fijo"] == 20000
    # 20.000 de 30.000 totales son "fijos" -> 66.6...%
    assert round(kpis["pct_ingresos_fijos"], 1) == 66.7


def test_kpis_calcula_porcentaje_de_cancelados(client):
    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client)

    # 1 realizado
    r = client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id,
        "fecha_programada": str(date.today()), "hora_programada": "09:00:00",
    })
    _completar(client, r.json()["id"], 10000)

    # 1 cancelado
    r = client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id,
        "fecha_programada": str(date.today()), "hora_programada": "11:00:00",
    })
    client.post(f"/trabajos/{r.json()['id']}/cancelar")

    # 1 todavía pendiente -> no debe contar ni como éxito ni como cancelación
    client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id,
        "fecha_programada": str(date.today()), "hora_programada": "15:00:00",
    })

    kpis = client.get("/dashboard/kpis", params={"periodo": "mes"}).json()

    assert kpis["trabajos_cancelados"] == 1
    assert kpis["trabajos_programados_periodo"] == 2  # realizado + cancelado, sin contar el pendiente
    assert kpis["pct_cancelados"] == 50.0
