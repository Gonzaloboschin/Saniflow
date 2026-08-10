# Arranque diario — SaniFlow

Cheat sheet para no tener que repensar esto cada vez. Todo se corre desde
`saniflow/backend/` salvo que se aclare lo contrario.

## 1. Levantar Postgres (WSL no lo arranca solo)
```bash
service postgresql start
```

## 2. Activar el entorno virtual
```bash
cd /mnt/c/Users/bosch/Desktop/srd-crm/saniflow/saniflow/backend
source .venv/bin/activate
```
Confirmá que el prompt te queda con `(.venv)` adelante.

## 3. Levantar el servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0
```
Abrir: `http://localhost:8000/docs`

Cortar con `Ctrl+C` cuando termines.

## 4. Rutina de git al final de cada sesión
```bash
git status              # revisar qué cambió (chequear que no aparezca .env)
git add .
git commit -m "descripción corta de lo que se hizo"
git push
```

---

## Comandos que se usan menos seguido, pero conviene tener a mano

**Recrear la base desde cero** (borra todo y vuelve a cargar el seed):
```bash
python scripts/seed_data.py
```

**Aplicar una migración nueva**, después de modificar algo en `app/models/`:
```bash
alembic revision --autogenerate -m "descripción del cambio"
alembic upgrade head
```

**Correr los tests**:
```bash
pytest tests/ -v
```

**Si WSL se reinició y `localhost:8000` no conecta desde el navegador de Windows**:
```bash
hostname -I     # usar esa IP en vez de localhost
```
