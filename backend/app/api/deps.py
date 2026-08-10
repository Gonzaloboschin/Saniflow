from fastapi import HTTPException, status


def not_found(entidad: str, entidad_id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entidad} {entidad_id} no encontrado")
