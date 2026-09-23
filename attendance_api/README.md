# API de Asistencia — Instituto Educativo

API REST construida con **FastAPI** + **SQLAlchemy** para gestionar el
fichaje (entrada/salida) y el registro de temas dictados por personal
docente y no docente.

## Estructura del proyecto

```
attendance_api/
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py
    ├── main.py              # Punto de entrada, registra los routers
    ├── database.py          # Engine, SessionLocal, Base, get_db
    ├── models.py             # Modelos SQLAlchemy (las 4 tablas)
    ├── schemas.py            # Esquemas Pydantic (entrada/salida)
    └── routers/
        ├── __init__.py
        ├── usuarios.py        # CRUD de Usuarios
        ├── materias.py        # CRUD de Materias
        ├── docente_materia.py # Asignaciones docente-materia + filtro por día
        └── asistencias.py     # Fichaje entrada/salida + carga de tema
```

## Modelo de datos

- **Usuarios**: `id_usuario`, `nombre`, `apellido`, `tipo_empleado` (`docente` / `no_docente`).
- **Materias**: `id_materia`, `nombre_materia`.
- **Docente_Materia**: relación N a N entre Usuarios y Materias, con
  `dia_semana` para soportar múltiples días por combinación docente-materia.
- **Asistencias**: núcleo de fichaje, con `id_materia` nullable (solo se
  usa en docentes) y `tema_dictado` nullable.

## Instalación y ejecución

```bash
cd attendance_api

# 1. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Levantar el servidor
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000` y la documentación
interactiva (Swagger UI) en `http://127.0.0.1:8000/docs`.

La base de datos SQLite (`asistencia.db`) se crea automáticamente al
iniciar la app. Para usar PostgreSQL/MySQL en producción, solo hay que
cambiar `SQLALCHEMY_DATABASE_URL` en `app/database.py`.

## Endpoints principales

### Usuarios (`/usuarios`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/usuarios/` | Crear usuario |
| GET | `/usuarios/` | Listar usuarios (filtro opcional `?tipo_empleado=`) |
| GET | `/usuarios/{id_usuario}` | Obtener un usuario |
| PUT | `/usuarios/{id_usuario}` | Actualizar usuario |
| DELETE | `/usuarios/{id_usuario}` | Eliminar usuario |

### Materias (`/materias`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/materias/` | Crear materia |
| GET | `/materias/` | Listar materias |
| GET | `/materias/{id_materia}` | Obtener una materia |
| DELETE | `/materias/{id_materia}` | Eliminar materia |

### Docente-Materia (`/docente-materia`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/docente-materia/` | Asignar una materia a un docente en un día específico |
| GET | `/docente-materia/` | Listar asignaciones (filtro opcional `?id_usuario=`) |
| GET | `/docente-materia/materias-hoy/{id_usuario}` | **Materias del docente para el día actual** |
| DELETE | `/docente-materia/{id_docente_materia}` | Eliminar una asignación |

### Asistencias (`/asistencias`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/asistencias/entrada` | Registrar fichaje de entrada |
| PUT | `/asistencias/salida/{id_asistencia}` | Registrar fichaje de salida |
| PUT | `/asistencias/tema/{id_asistencia}` | **Cargar materia + tema dictado (solo docentes)** |
| GET | `/asistencias/` | Listar asistencias (filtro opcional `?id_usuario=`) |
| GET | `/asistencias/{id_asistencia}` | Obtener una asistencia puntual |

## Flujo típico de uso (docente)

1. `POST /usuarios/` → crear al docente.
2. `POST /materias/` → crear las materias que dicta.
3. `POST /docente-materia/` → asignarle materias por día (ej: "Matemática" los "Lunes").
4. Al llegar al instituto: `POST /asistencias/entrada` con su `id_usuario`
   (sin materia todavía) → devuelve `id_asistencia`.
5. Desde su celular, antes de empezar la clase: `GET /docente-materia/materias-hoy/{id_usuario}`
   para ver qué materias le tocan hoy.
6. `PUT /asistencias/tema/{id_asistencia}` con la materia elegida y el
   tema dictado → el backend valida que esa materia esté asignada a ese
   docente en el día actual.
7. Al retirarse: `PUT /asistencias/salida/{id_asistencia}`.

## Flujo típico de uso (no docente)

1. `POST /usuarios/` con `tipo_empleado: "no_docente"`.
2. `POST /asistencias/entrada` con su `id_usuario` (nunca lleva materia,
   se ignora aunque se envíe).
3. `PUT /asistencias/salida/{id_asistencia}` al retirarse.

## Notas de diseño

- El fichaje evita duplicados: no permite una nueva entrada si el
  usuario ya tiene una abierta (sin `fecha_hora_salida`).
- La validación de "materia del día" se hace consultando directamente
  `Docente_Materia` (Opción A del enunciado), sin depender de tablas de
  calendario adicionales.
- Los esquemas Pydantic usan `model_config = ConfigDict(from_attributes=True)`
  (Pydantic v2) para serializar directamente los objetos ORM.
- Para producción se recomienda reemplazar `Base.metadata.create_all`
  por migraciones con **Alembic**.
