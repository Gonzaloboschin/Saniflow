from pydantic import BaseModel, ConfigDict


class TecnicoBase(BaseModel):
    nombre: str
    telefono: str | None = None
    email: str | None = None
    activo: bool = True


class TecnicoCreate(TecnicoBase):
    pass


class TecnicoUpdate(BaseModel):
    nombre: str | None = None
    telefono: str | None = None
    email: str | None = None
    activo: bool | None = None


class TecnicoOut(TecnicoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
