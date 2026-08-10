from datetime import date, timedelta


def _crear_servicio(client):
    r = client.post("/servicios", json={"nombre": "Desinsectación", "precio_base": 15000})
    assert r.status_code == 201
    return r.json()["id"]


def _crear_cliente(client):
    r = client.post("/clientes", json={"nombre": "Cliente de prueba"})
    assert r.status_code == 201
    return r.json()["id"]


def test_crear_y_completar_trabajo_sin_contrato(client):
    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client)

    r = client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id,
        "fecha_programada": str(date.today()), "hora_programada": "09:00:00",
    })
    assert r.status_code == 201
    trabajo_id = r.json()["id"]
    assert r.json()["estado"] == "pendiente"

    r = client.post(f"/trabajos/{trabajo_id}/completar", json={
        "hora_inicio": "09:00:00", "hora_fin": "09:40:00",
        "monto": 15000, "costo": 5000,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["trabajo"]["estado"] == "realizado"
    assert data["trabajo"]["duracion_min"] == 40
    assert data["proximo_trabajo_generado"] is None  # no hay contrato -> no se auto-agenda


def test_completar_trabajo_con_contrato_genera_el_proximo(client):
    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client)

    r = client.post("/contratos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id, "frecuencia": "mensual",
        "fecha_inicio": str(date.today() - timedelta(days=30)),
    })
    assert r.status_code == 201
    contrato_id = r.json()["id"]

    r = client.post("/trabajos", json={
        "cliente_id": cliente_id, "servicio_id": servicio_id, "contrato_id": contrato_id,
        "fecha_programada": str(date.today()), "hora_programada": "10:00:00",
    })
    trabajo_id = r.json()["id"]

    r = client.post(f"/trabajos/{trabajo_id}/completar", json={
        "hora_inicio": "10:00:00", "hora_fin": "10:30:00", "monto": 15000, "costo": 5000,
    })
    data = r.json()
    proximo = data["proximo_trabajo_generado"]
    assert proximo is not None
    assert proximo["estado"] == "pendiente"
    assert proximo["fecha_programada"] == str(date.today() + timedelta(days=30))


def test_cliente_en_riesgo_por_reclamos_frecuentes(client):
    cliente_id = _crear_cliente(client)
    for _ in range(2):
        r = client.post("/interacciones", json={
            "cliente_id": cliente_id, "tipo": "reclamo", "motivo": "Reaparición de plaga",
        })
        assert r.status_code == 201

    r = client.get("/clientes/en-riesgo")
    assert r.status_code == 200
    ids_en_riesgo = [c["cliente_id"] for c in r.json()]
    assert cliente_id in ids_en_riesgo


def test_problemas_recurrentes_por_etiquetas(client):
    servicio_id = _crear_servicio(client)
    cliente_id = _crear_cliente(client)

    for _ in range(3):
        r = client.post("/trabajos", json={
            "cliente_id": cliente_id, "servicio_id": servicio_id,
            "fecha_programada": str(date.today()), "hora_programada": "09:00:00",
        })
        trabajo_id = r.json()["id"]
        client.post(f"/trabajos/{trabajo_id}/completar", json={
            "hora_inicio": "09:00:00", "hora_fin": "09:30:00", "monto": 15000, "costo": 5000,
            "etiquetas": ["reaparición cucarachas"],
        })

    r = client.get(f"/clientes/{cliente_id}/problemas-recurrentes")
    assert r.status_code == 200
    etiquetas = {p["etiqueta"]: p["ocurrencias"] for p in r.json()}
    assert etiquetas.get("reaparición cucarachas") == 3
