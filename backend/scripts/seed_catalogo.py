"""
Carga el catálogo de servicios (necesario para que la importación de
clientes pueda crear los contratos de los clientes "Fijos"), sin ningún
cliente, trabajo, técnico ni dato de prueba.

Pensado para correr una sola vez, contra una base recién creada/limpiada.
Se puede correr de nuevo sin problema: si un servicio ya existe (por
nombre), no lo duplica.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal, engine, Base
from app.models.servicio import Servicio

SERVICIOS = [
    {"nombre": "Desinsectación general", "descripcion": "Cucarachas, hormigas, insectos rastreros",
     "precio_base": 15000, "color": "#0F5C56"},
    {"nombre": "Desratización", "descripcion": "Control de roedores", "precio_base": 18000, "color": "#8B5E34"},
    {"nombre": "Sanitización / Desinfección", "descripcion": "Desinfección de superficies y ambientes",
     "precio_base": 12000, "color": "#2F9E6E"},
    {"nombre": "Control de plagas", "descripcion": "Cucarachas y hormigas en comercios",
     "precio_base": 14000, "color": "#C2542B"},
    {"nombre": "Fumigación de espacios verdes", "descripcion": "Jardines y áreas exteriores",
     "precio_base": 20000, "color": "#3E7CB1"},
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    creados = 0
    for datos in SERVICIOS:
        existe = db.query(Servicio).filter(Servicio.nombre == datos["nombre"]).first()
        if existe:
            continue
        db.add(Servicio(**datos))
        creados += 1
    db.commit()
    db.close()
    print(f"Catálogo listo. {creados} servicios nuevos creados (los que ya existían se dejaron sin tocar).")


if __name__ == "__main__":
    run()