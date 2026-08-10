# SaniFlow API

Backend de gestión de trabajos y clientes para una empresa de desinfecciones
(desinsectación, desratización, sanitización, control de plagas, fumigación).

Stack: **Python 3.12 + FastAPI + SQLAlchemy + PostgreSQL + Alembic**.

## Puesta en marcha local

### 1. Requisitos
- Python 3.11+
- PostgreSQL 14+ corriendo localmente (o accesible por red)

### 2. Crear la base de datos
```bash
psql -c "CREATE USER saniflow WITH PASSWORD 'saniflow';"
psql -c "CREATE DATABASE saniflow OWNER saniflow;"
```

### 3. Entorno virtual y dependencias
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Variables de entorno
```bash
cp .env.example .env
# Editar .env si tu usuario/contraseña/puerto de Postgres son distintos
```

### 5. Migraciones
```bash
alembic upgrade head
```

### 6. Datos de prueba (opcional, recomendado para demo)
```bash
python scripts/seed_data.py
```

### 7. Levantar el servidor
```bash
uvicorn app.main:app --reload
```

La API queda en `http://localhost:8000`. Documentación interactiva
autogenerada (Swagger) en `http://localhost:8000/docs`.

## Correr los tests
```bash
pytest tests/ -v
```
Los tests corren contra SQLite en memoria — no tocan la base de desarrollo.

## Estructura

```
app/
├── core/       config y conexión a la base de datos
├── models/     tablas (SQLAlchemy) — el modelo de datos
├── schemas/    contratos de entrada/salida de la API (Pydantic)
├── crud/       acceso a datos, sin lógica de negocio
├── services/   lógica de negocio real (completar trabajo, detectar riesgo, KPIs)
└── api/routers/ endpoints HTTP, delgados: reciben, delegan, devuelven
```

La regla de dependencia es: `routers → services → crud → models`.
Los routers no tocan SQLAlchemy directamente, y los services no saben
nada de HTTP. Eso es lo que permite, por ejemplo, testear
`completar_trabajo` sin levantar un servidor.

## Ver también
- `../docs/MODELO_DE_DATOS.md` — entidades y relaciones
- `../docs/ARQUITECTURA.md` — por qué está armado así
- `../docs/ROADMAP.md` — qué sigue
