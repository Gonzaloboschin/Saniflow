from pydantic import BaseModel, ConfigDict


class TecnicoBase(BaseModel):
    nombre: str
    telefono: str | None = None
    activo: bool = True


class TecnicoCreate(TecnicoBase):
    pass


class TecnicoOut(TecnicoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
