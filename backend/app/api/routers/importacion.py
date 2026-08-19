import io

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.importacion import FilaImportacion, FilaImportacionPreview, ResumenImportacion
from app.services import importacion_service

router = APIRouter(prefix="/clientes/importar", tags=["importación"])


def _a_preview(p) -> FilaImportacionPreview:
    return FilaImportacionPreview(
        fila=p.fila,
        datos=p.raw,
        estado=p.estado,
        mensajes=p.mensajes,
        tipo_resuelto=p.tipo.value if hasattr(p.tipo, "value") else str(p.tipo),
        es_fijo=p.servicio_id is not None,
        servicio_resuelto=p.servicio_nombre,
    )


@router.get("/plantilla")
def descargar_plantilla():
    contenido = importacion_service.generar_plantilla()
    return StreamingResponse(
        io.BytesIO(contenido),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_clientes_saniflow.xlsx"},
    )


@router.post("/previsualizar", response_model=list[FilaImportacionPreview])
async def previsualizar(archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    contenido = await archivo.read()
    filas = importacion_service.previsualizar(db, contenido)
    return [_a_preview(f) for f in filas]


@router.post("/confirmar", response_model=ResumenImportacion)
def confirmar(filas: list[FilaImportacion], db: Session = Depends(get_db)):
    creados, contratos_creados, omitidos, detalles = importacion_service.confirmar(db, filas)
    return ResumenImportacion(
        creados=creados, contratos_creados=contratos_creados, omitidos=omitidos,
        detalles=[_a_preview(d) for d in detalles],
    )
