"""
Configuración de la base de datos.

Local:
    Usa SQLite mediante asistencia.db

Render / Producción:
    Usa PostgreSQL mediante la variable de entorno DATABASE_URL
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Render tendrá DATABASE_URL.
# En local no existe, entonces seguimos usando SQLite.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render puede entregar la URL comenzando con postgres://
    # SQLAlchemy + psycopg usan postgresql+psycopg://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    SQLALCHEMY_DATABASE_URL = DATABASE_URL

    # PostgreSQL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

else:
    # SQLite para desarrollo local
    SQLALCHEMY_DATABASE_URL = "sqlite:///./asistencia.db"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesión de DB y la cierra al final."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()