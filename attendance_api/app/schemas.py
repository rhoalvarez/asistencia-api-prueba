"""
Esquemas Pydantic usados para validar entradas y serializar salidas.
Se separan en Base / Create / Update / Out para mantener el CRUD prolijo.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from .models import TipoEmpleado


# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------
class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    tipo_empleado: TipoEmpleado


class LoginRequest(BaseModel):
    usuario: str
    contrasenia: str


class UsuarioCreate(UsuarioBase):
    usuario: str
    contrasenia: str


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    tipo_empleado: Optional[TipoEmpleado] = None
    usuario: Optional[str] = None
    contrasenia: Optional[str] = None


class UsuarioOut(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    id_usuario: int


# ---------------------------------------------------------------------------
# Materia
# ---------------------------------------------------------------------------
class MateriaBase(BaseModel):
    nombre_materia: str


class MateriaCreate(MateriaBase):
    pass


class MateriaOut(MateriaBase):
    model_config = ConfigDict(from_attributes=True)
    id_materia: int


# ---------------------------------------------------------------------------
# Docente_Materia
# ---------------------------------------------------------------------------
DIAS_VALIDOS = {
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
}


class DocenteMateriaBase(BaseModel):
    id_usuario: int
    id_materia: int
    dia_semana: str

    @field_validator("dia_semana")
    @classmethod
    def validar_dia(cls, v: str) -> str:
        if v not in DIAS_VALIDOS:
            raise ValueError(
                f"dia_semana debe ser uno de: {sorted(DIAS_VALIDOS)}"
            )
        return v


class DocenteMateriaCreate(DocenteMateriaBase):
    pass


class DocenteMateriaOut(DocenteMateriaBase):
    model_config = ConfigDict(from_attributes=True)
    id_docente_materia: int


class MateriaDelDiaOut(BaseModel):
    """Respuesta del endpoint de materias filtradas por día actual."""
    id_docente_materia: int
    id_materia: int
    nombre_materia: str
    dia_semana: str


# ---------------------------------------------------------------------------
# Asistencia
# ---------------------------------------------------------------------------
class AsistenciaEntradaCreate(BaseModel):
    id_usuario: int

    # Opcional: si la terminal ya sabe qué materia va a dictar
    # el docente en el momento de fichar, se puede mandar.
    # Si no, se completa después con el endpoint de carga de tema.
    id_materia: Optional[int] = None


class AsistenciaSalidaUpdate(BaseModel):
    # Si no se envía, el backend usa datetime.now()
    fecha_hora_salida: Optional[datetime] = None


class AsistenciaTemaUpdate(BaseModel):
    id_materia: int
    tema_dictado: str


class AsistenciaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_asistencia: int
    id_usuario: int
    id_materia: Optional[int] = None
    fecha_hora_entrada: datetime
    fecha_hora_salida: Optional[datetime] = None
    tema_dictado: Optional[str] = None