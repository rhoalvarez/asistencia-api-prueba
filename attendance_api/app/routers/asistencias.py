from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from .docente_materia import DIAS_SEMANA_ES

router = APIRouter(prefix="/asistencias", tags=["Asistencias"])


@router.post(
    "/entrada", response_model=schemas.AsistenciaOut, status_code=status.HTTP_201_CREATED
)
def registrar_entrada(datos: schemas.AsistenciaEntradaCreate, db: Session = Depends(get_db)):
    """
    Registra el fichaje de entrada de cualquier empleado.
    - No docente: nunca lleva materia (se fuerza a NULL aunque llegue algo).
    - Docente: la materia es opcional en este paso; puede completarse
      después con PUT /asistencias/tema/{id_asistencia}.
    """
    usuario = (
        db.query(models.Usuario).filter(models.Usuario.id_usuario == datos.id_usuario).first()
    )
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Evita fichar una entrada nueva si ya hay una abierta (sin salida)
    entrada_abierta = (
        db.query(models.Asistencia)
        .filter(
            models.Asistencia.id_usuario == datos.id_usuario,
            models.Asistencia.fecha_hora_salida.is_(None),
        )
        .first()
    )
    if entrada_abierta:
        raise HTTPException(
            status_code=400,
            detail=(
                f"El usuario ya tiene una entrada abierta "
                f"(id_asistencia={entrada_abierta.id_asistencia}) sin salida marcada"
            ),
        )

    id_materia = None
    if usuario.tipo_empleado == models.TipoEmpleado.docente and datos.id_materia is not None:
        materia = (
            db.query(models.Materia)
            .filter(models.Materia.id_materia == datos.id_materia)
            .first()
        )
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")
        id_materia = datos.id_materia
    # Si es no_docente, id_materia queda en None sin importar lo que se envíe.

    nueva_asistencia = models.Asistencia(
        id_usuario=datos.id_usuario,
        id_materia=id_materia,
        fecha_hora_entrada=datetime.now(),
        fecha_hora_salida=None,
        tema_dictado=None,
    )
    db.add(nueva_asistencia)
    db.commit()
    db.refresh(nueva_asistencia)
    return nueva_asistencia


@router.put("/salida/{id_asistencia}", response_model=schemas.AsistenciaOut)
def registrar_salida(
    id_asistencia: int,
    datos: schemas.AsistenciaSalidaUpdate,
    db: Session = Depends(get_db),
):
    """Marca la salida de un fichaje ya existente."""
    asistencia = (
        db.query(models.Asistencia)
        .filter(models.Asistencia.id_asistencia == id_asistencia)
        .first()
    )
    if not asistencia:
        raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")

    if asistencia.fecha_hora_salida is not None:
        raise HTTPException(status_code=400, detail="Este registro ya tiene una salida marcada")

    asistencia.fecha_hora_salida = datos.fecha_hora_salida or datetime.now()
    db.commit()
    db.refresh(asistencia)
    return asistencia


@router.put("/tema/{id_asistencia}", response_model=schemas.AsistenciaOut)
def cargar_tema_dictado(
    id_asistencia: int,
    datos: schemas.AsistenciaTemaUpdate,
    db: Session = Depends(get_db),
):
    """
    Exclusivo para docentes. Actualiza un registro de asistencia YA
    existente (donde el docente ya marcó entrada) asignándole la materia
    y el tema dictado, validando que esa materia le corresponda al
    docente en el día actual según Docente_Materia.
    """
    asistencia = (
        db.query(models.Asistencia)
        .filter(models.Asistencia.id_asistencia == id_asistencia)
        .first()
    )
    if not asistencia:
        raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")

    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.id_usuario == asistencia.id_usuario)
        .first()
    )
    if usuario.tipo_empleado != models.TipoEmpleado.docente:
        raise HTTPException(
            status_code=400, detail="Solo los docentes pueden cargar tema dictado"
        )

    dia_actual = DIAS_SEMANA_ES[datetime.now().weekday()]

    asignacion_valida = (
        db.query(models.DocenteMateria)
        .filter(
            models.DocenteMateria.id_usuario == usuario.id_usuario,
            models.DocenteMateria.id_materia == datos.id_materia,
            models.DocenteMateria.dia_semana == dia_actual,
        )
        .first()
    )
    if not asignacion_valida:
        raise HTTPException(
            status_code=400,
            detail=f"La materia indicada no está asignada a este docente para el día {dia_actual}",
        )

    asistencia.id_materia = datos.id_materia
    asistencia.tema_dictado = datos.tema_dictado
    db.commit()
    db.refresh(asistencia)
    return asistencia


@router.get("/", response_model=List[schemas.AsistenciaOut])
def listar_asistencias(id_usuario: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Asistencia)
    if id_usuario is not None:
        query = query.filter(models.Asistencia.id_usuario == id_usuario)
    return query.order_by(models.Asistencia.fecha_hora_entrada.desc()).all()


@router.get("/{id_asistencia}", response_model=schemas.AsistenciaOut)
def obtener_asistencia(id_asistencia: int, db: Session = Depends(get_db)):
    asistencia = (
        db.query(models.Asistencia)
        .filter(models.Asistencia.id_asistencia == id_asistencia)
        .first()
    )
    if not asistencia:
        raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
    return asistencia
