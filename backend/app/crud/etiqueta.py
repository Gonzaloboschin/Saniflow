from sqlalchemy.orm import Session

from app.models.etiqueta import Etiqueta


def get_or_create_many(db: Session, nombres: list[str]) -> list[Etiqueta]:
    """Busca etiquetas por nombre y crea las que no existan todavía.
    Se usa al completar un trabajo o registrar un reclamo con etiquetas libres."""
    if not nombres:
        return []
    nombres_norm = {n.strip().lower() for n in nombres if n.strip()}
    existentes = db.query(Etiqueta).filter(Etiqueta.nombre.in_(nombres_norm)).all()
    existentes_por_nombre = {e.nombre: e for e in existentes}

    resultado = []
    for nombre in nombres_norm:
        if nombre in existentes_por_nombre:
            resultado.append(existentes_por_nombre[nombre])
        else:
            nueva = Etiqueta(nombre=nombre)
            db.add(nueva)
            db.flush()  # asigna id sin cerrar la transacción
            resultado.append(nueva)
    return resultado
