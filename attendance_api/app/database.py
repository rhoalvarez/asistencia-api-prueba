"""
Configuración de la base de datos.

Por defecto se usa SQLite para que el proyecto corra sin dependencias
externas. Para producción, solo hay que cambiar SQLALCHEMY_DATABASE_URL
por una cadena de conexión de PostgreSQL / MySQL, por ejemplo:

    postgresql://usuario:password@localhost:5432/asistencia_db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./asistencia.db"

# connect_args solo es necesario para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesión de DB y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
