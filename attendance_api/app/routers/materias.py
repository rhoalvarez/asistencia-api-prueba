from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/materias", tags=["Materias"])


@router.post("/", response_model=schemas.MateriaOut, status_code=status.HTTP_201_CREATED)
def crear_materia(materia: schemas.MateriaCreate, db: Session = Depends(get_db)):
    nueva_materia = models.Materia(**materia.model_dump())
    db.add(nueva_materia)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe una materia con ese nombre")
    db.refresh(nueva_materia)
    return nueva_materia


@router.get("/", response_model=List[schemas.MateriaOut])
def listar_materias(db: Session = Depends(get_db)):
    return db.query(models.Materia).all()


@router.get("/{id_materia}", response_model=schemas.MateriaOut)
def obtener_materia(id_materia: int, db: Session = Depends(get_db)):
    materia = db.query(models.Materia).filter(models.Materia.id_materia == id_materia).first()
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return materia


@router.delete("/{id_materia}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_materia(id_materia: int, db: Session = Depends(get_db)):
    materia = db.query(models.Materia).filter(models.Materia.id_materia == id_materia).first()
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    db.delete(materia)
    db.commit()
    return None
