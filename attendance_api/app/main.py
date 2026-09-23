from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import usuarios, materias, docente_materia, asistencias

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Asistencia - Instituto Educativo",
    description=(
        "Sistema de fichaje y control de asistencia para personal "
        "docente y no docente."
    ),
    version="1.0.0",
)

# Permitir que React se conecte con la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(materias.router)
app.include_router(docente_materia.router)
app.include_router(asistencias.router)


@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "API de Asistencia funcionando correctamente"}