"""
Modelos ORM (SQLAlchemy) que reflejan las 4 tablas del sistema:

Usuarios (1) ----< Docente_Materia >---- (1) Materias
Usuarios (1) ----< Asistencias >---- (0..1) Materias
"""

import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SqlEnum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class TipoEmpleado(str, enum.Enum):
    docente = "docente"
    no_docente = "no_docente"


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    usuario = Column(String(50), nullable=True, unique=True)
    contrasenia = Column(String(100), nullable=True)
    tipo_empleado = Column(SqlEnum(TipoEmpleado), nullable=False)

    materias_asignadas = relationship(
        "DocenteMateria", back_populates="usuario", cascade="all, delete-orphan"
    )
    asistencias = relationship(
        "Asistencia", back_populates="usuario", cascade="all, delete-orphan"
    )


class Materia(Base):
    __tablename__ = "materias"

    id_materia = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_materia = Column(String(150), nullable=False, unique=True)

    docentes_asignados = relationship(
        "DocenteMateria", back_populates="materia", cascade="all, delete-orphan"
    )
    asistencias = relationship("Asistencia", back_populates="materia")


class DocenteMateria(Base):
    """
    Tabla intermedia Usuario <-> Materia con soporte de múltiples días.
    Un mismo docente puede tener la misma materia en varios días, por eso
    la clave real de unicidad es (id_usuario, id_materia, dia_semana).
    """

    __tablename__ = "docente_materia"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario", "id_materia", "dia_semana", name="uq_docente_materia_dia"
        ),
    )

    id_docente_materia = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_materia = Column(Integer, ForeignKey("materias.id_materia"), nullable=False)
    dia_semana = Column(String(20), nullable=False)  # 'Lunes', 'Martes', ...

    usuario = relationship("Usuario", back_populates="materias_asignadas")
    materia = relationship("Materia", back_populates="docentes_asignados")


class Asistencia(Base):
    __tablename__ = "asistencias"

    id_asistencia = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_materia = Column(Integer, ForeignKey("materias.id_materia"), nullable=True)
    fecha_hora_entrada = Column(DateTime, nullable=False)
    fecha_hora_salida = Column(DateTime, nullable=True)
    tema_dictado = Column(Text, nullable=True)

    usuario = relationship("Usuario", back_populates="asistencias")
    materia = relationship("Materia", back_populates="asistencias")
