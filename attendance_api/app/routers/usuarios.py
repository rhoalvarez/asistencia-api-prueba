from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    nuevo_usuario = models.Usuario(**usuario.model_dump())
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.get("/", response_model=List[schemas.UsuarioOut])
def listar_usuarios(
    tipo_empleado: models.TipoEmpleado | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Usuario)
    if tipo_empleado is not None:
        query = query.filter(models.Usuario.tipo_empleado == tipo_empleado)
    return query.all()


@router.post("/login")
def login(
    datos: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    usuario_encontrado = (
        db.query(models.Usuario)
        .filter(models.Usuario.usuario == datos.usuario)
        .first()
    )

    if not usuario_encontrado:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    if usuario_encontrado.contrasenia != datos.contrasenia:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    return {
        "usuario": {
            "id": usuario_encontrado.id_usuario,
            "usuario": usuario_encontrado.usuario,
            "nombre": (
                f"{usuario_encontrado.nombre} "
                f"{usuario_encontrado.apellido}"
            ),
            "rol": usuario_encontrado.tipo_empleado.value
        }
    }

@router.get("/{id_usuario}", response_model=schemas.UsuarioOut)
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{id_usuario}", response_model=schemas.UsuarioOut)
def actualizar_usuario(
    id_usuario: int, datos: schemas.UsuarioUpdate, db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return None

