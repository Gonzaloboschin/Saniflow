"""
Carga datos de ejemplo realistas para poder demostrar el sistema:
- catálogo de servicios y técnicos
- clientes con distinto perfil (uno con contrato mensual, uno que bajó de
  frecuencia, uno con reclamos recurrentes por el mismo problema)
- trabajos pendientes de hoy/mañana y un historial de varios meses
- interacciones (reclamos/consultas) con etiquetas, para poblar las
  alertas de "clientes en riesgo" y "problemas recurrentes"

Se puede correr las veces que haga falta: primero limpia las tablas.
"""
import random
import sys
from pathlib import Path
from datetime import date, timedelta, time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal, engine, Base
from app.models.servicio import Servicio
from app.models.tecnico import Tecnico
from app.models.cliente import Cliente, TipoCliente
from app.models.contrato import Contrato, FrecuenciaContrato
from app.models.trabajo import Trabajo, EstadoTrabajo, PrioridadTrabajo
from app.models.interaccion import Interaccion, TipoInteraccion
from app.models.etiqueta import Etiqueta
import sys
from pathlib import Path

random.seed(7)


def limpiar(db):
    for modelo in [Trabajo, Interaccion, Contrato, Cliente, Etiqueta, Tecnico, Servicio]:
        db.query(modelo).delete()
    db.commit()


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    limpiar(db)

    servicios = [
        Servicio(nombre="Desinsectación general", descripcion="Cucarachas, hormigas, insectos rastreros",
                  precio_base=15000, color="#0F5C56"),
        Servicio(nombre="Desratización", descripcion="Control de roedores", precio_base=18000, color="#8B5E34"),
        Servicio(nombre="Sanitización / Desinfección", descripcion="Desinfección de superficies y ambientes",
                  precio_base=12000, color="#2F9E6E"),
        Servicio(nombre="Control de plagas", descripcion="Cucarachas y hormigas en comercios",
                  precio_base=14000, color="#C2542B"),
        Servicio(nombre="Fumigación de espacios verdes", descripcion="Jardines y áreas exteriores",
                  precio_base=20000, color="#3E7CB1"),
    ]
    db.add_all(servicios)

    tecnicos = [Tecnico(nombre=n) for n in ["Martín Ibáñez", "Lucas Peralta", "Equipo A", "Equipo B"]]
    db.add_all(tecnicos)
    db.commit()

    localidades = ["Ciudad, San Rafael", "Cuadro Nacional", "Rama Caída", "Villa 25 de Mayo", "Las Paredes"]
    calles = ["Av. Bartolomé Mitre", "San Martín", "Day Sur", "Comandante Salas", "Barcala", "Chile"]

    def direccion():
        return f"{random.choice(calles)} {100 + random.randint(0, 2900)}, {random.choice(localidades)}"

    def telefono():
        return f"260 4{random.randint(100000, 999999)}"

    # --- Clientes con distintos perfiles, a propósito ---
    cliente_fiel = Cliente(nombre="Farmacia del Sol", tipo=TipoCliente.comercio,
                            telefono=telefono(), direccion=direccion(), localidad="Ciudad, San Rafael")
    cliente_bajo_frecuencia = Cliente(nombre="Restó La Parrilla", tipo=TipoCliente.comercio,
                                       telefono=telefono(), direccion=direccion(), localidad="Rama Caída")
    cliente_reclamos = Cliente(nombre="Hotel Rincón", tipo=TipoCliente.comercio,
                                telefono=telefono(), direccion=direccion(), localidad="Cuadro Nacional")
    cliente_particular = Cliente(nombre="Sra. Beatriz Coria", tipo=TipoCliente.particular,
                                  telefono=telefono(), direccion=direccion(), localidad="Villa 25 de Mayo")

    nombres_generico = ["Bodega Los Álamos", "Consultorio Dr. Funes", "Panadería San José", "Familia Ortega",
                         "Kiosco 24hs", "Colegio San Rafael", "Sr. Daniel Vega", "Supermercado Norte"]
    clientes_genericos = [
        Cliente(nombre=n, tipo=random.choice(list(TipoCliente)), telefono=telefono(),
                direccion=direccion(), localidad=random.choice(localidades))
        for n in nombres_generico
    ]

    todos_clientes = [cliente_fiel, cliente_bajo_frecuencia, cliente_reclamos, cliente_particular] + clientes_genericos
    db.add_all(todos_clientes)
    db.commit()

    # --- Contratos ---
    contrato_fiel = Contrato(
        cliente_id=cliente_fiel.id, servicio_id=servicios[0].id,
        frecuencia=FrecuenciaContrato.mensual, precio_acordado=15000,
        fecha_inicio=date.today() - timedelta(days=200),
    )
    # Este cliente tenía contrato mensual y se dio de baja hace poco para pasar a "a demanda":
    # así se ve el cambio de frecuencia en el historial de contratos.
    contrato_viejo = Contrato(
        cliente_id=cliente_bajo_frecuencia.id, servicio_id=servicios[3].id,
        frecuencia=FrecuenciaContrato.mensual, precio_acordado=14000,
        fecha_inicio=date.today() - timedelta(days=300),
        fecha_fin=date.today() - timedelta(days=60),
        activo=False,
    )
    contrato_nuevo = Contrato(
        cliente_id=cliente_bajo_frecuencia.id, servicio_id=servicios[3].id,
        frecuencia=FrecuenciaContrato.a_demanda, precio_acordado=14000,
        fecha_inicio=date.today() - timedelta(days=59),
    )
    contrato_reclamos = Contrato(
        cliente_id=cliente_reclamos.id, servicio_id=servicios[1].id,
        frecuencia=FrecuenciaContrato.mensual, precio_acordado=18000,
        fecha_inicio=date.today() - timedelta(days=150),
    )
    db.add_all([contrato_fiel, contrato_viejo, contrato_nuevo, contrato_reclamos])
    db.commit()

    codigo_n = 1

    def prox_codigo():
        nonlocal codigo_n
        c = f"T-{codigo_n:05d}"
        codigo_n += 1
        return c

    # --- Historial de trabajos realizados (últimos 12 meses, variado) ---
    detalle_generico = "Aplicación de producto según protocolo estándar del servicio."
    todos = [cliente_fiel, cliente_bajo_frecuencia, cliente_reclamos, cliente_particular] + clientes_genericos

    for _ in range(55):
        cliente = random.choice(todos)
        servicio = random.choice(servicios)
        d = date.today() - timedelta(days=random.randint(1, 365))
        hi = time(hour=random.randint(8, 16), minute=random.choice([0, 30]))
        dur = random.randint(30, 110)
        monto = round(float(servicio.precio_base) * random.uniform(0.85, 1.2) / 100) * 100
        costo = round(monto * random.uniform(0.25, 0.45))
        db.add(Trabajo(
            codigo=prox_codigo(), cliente_id=cliente.id, servicio_id=servicio.id,
            tecnico_id=random.choice(tecnicos).id,
            fecha_programada=d, hora_programada=hi, estado=EstadoTrabajo.realizado,
            hora_inicio=hi, hora_fin=time((hi.hour + dur // 60) % 24, (hi.minute + dur % 60) % 60),
            duracion_min=dur, monto=monto, costo=costo, detalle_trabajo=detalle_generico,
            fecha_realizado=d,
        ))

    # Historial específico del cliente con problema recurrente: reaparición
    # de roedores en la cocina, 4 veces en el año -> debe saltar como
    # "problema recurrente" al consultar su ficha.
    etiqueta_recurrente = Etiqueta(nombre="reaparición de roedores en cocina")
    db.add(etiqueta_recurrente)
    db.flush()
    for i in range(4):
        d = date.today() - timedelta(days=30 * (i + 1))
        t = Trabajo(
            codigo=prox_codigo(), cliente_id=cliente_reclamos.id, servicio_id=servicios[1].id,
            tecnico_id=tecnicos[0].id, contrato_id=contrato_reclamos.id,
            fecha_programada=d, hora_programada=time(10, 0), estado=EstadoTrabajo.realizado,
            hora_inicio=time(10, 0), hora_fin=time(11, 0), duracion_min=60,
            monto=18000, costo=6000, detalle_trabajo="Cebos en cocina y depósito. Cliente reporta actividad reciente.",
            fecha_realizado=d,
        )
        t.etiquetas.append(etiqueta_recurrente)
        db.add(t)

    # --- Reclamos: 3 en los últimos 60 días -> debe disparar "cliente en riesgo" ---
    for i in range(3):
        db.add(Interaccion(
            cliente_id=cliente_reclamos.id,
            tipo=TipoInteraccion.reclamo,
            motivo="Reaparición de roedores luego del servicio",
            descripcion="El cliente llamó reportando actividad de roedores a los pocos días del último tratamiento.",
            resuelto=(i < 2),
            resolucion="Se reprogramó visita de refuerzo sin costo." if i < 2 else None,
            registrado_por="Administración",
        ))
    db.flush()
    # etiquetamos los reclamos con la misma etiqueta para que se sumen al conteo
    reclamos_cliente = db.query(Interaccion).filter(Interaccion.cliente_id == cliente_reclamos.id).all()
    for r in reclamos_cliente:
        r.etiquetas.append(etiqueta_recurrente)

    # Una consulta común (no reclamo) para otro cliente, sin drama
    db.add(Interaccion(
        cliente_id=cliente_fiel.id, tipo=TipoInteraccion.consulta,
        motivo="Consulta por servicio adicional en depósito",
        descripcion="Pregunta si se puede sumar el depósito trasero al servicio mensual.",
        resuelto=True, resolucion="Se cotizó como servicio adicional, cliente evaluando.",
        registrado_por="Administración",
    ))

    db.commit()

    # --- Pendientes: 6 para hoy, 4 para los próximos días ---
    horas_hoy = [time(9, 0), time(10, 30), time(11, 30), time(14, 0), time(16, 0), time(17, 30)]
    for i, hi in enumerate(horas_hoy):
        cliente = random.choice(todos)
        servicio = random.choice(servicios)
        db.add(Trabajo(
            codigo=prox_codigo(), cliente_id=cliente.id, servicio_id=servicio.id,
            tecnico_id=random.choice(tecnicos).id,
            fecha_programada=date.today(), hora_programada=hi,
            prioridad=PrioridadTrabajo.urgente if i == 0 else PrioridadTrabajo.normal,
            estado=EstadoTrabajo.pendiente,
        ))

    for i in range(4):
        cliente = random.choice(todos)
        servicio = random.choice(servicios)
        db.add(Trabajo(
            codigo=prox_codigo(), cliente_id=cliente.id, servicio_id=servicio.id,
            tecnico_id=random.choice(tecnicos).id,
            fecha_programada=date.today() + timedelta(days=random.randint(1, 5)),
            hora_programada=time(random.choice([9, 10, 11, 14, 16]), 0),
            estado=EstadoTrabajo.pendiente,
        ))

    db.commit()
    db.close()
    print("Seed cargado correctamente.")


if __name__ == "__main__":
    run()
