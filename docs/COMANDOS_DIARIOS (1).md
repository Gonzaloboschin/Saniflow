# Arranque diario — SaniFlow

## El atajo (usar esto siempre que se pueda)

Desde la raíz del proyecto (`saniflow/`):

```bash
./dev.sh
```
Levanta Postgres, activa el venv, y levanta backend + frontend juntos.
Backend en `http://localhost:8000/docs`, frontend en `http://localhost:5173`.
**Ctrl+C corta los dos** de una.

Al terminar de trabajar, para guardar y subir los cambios:
```bash
./save.sh "descripción corta de lo que se hizo"
```
Hace `git add` + `commit` + `push` en un solo paso. Si por error detecta
un archivo `.env` entre los cambios, **frena y no sube nada** — es una
red de seguridad para no subir contraseñas sin querer.

La primera vez que se usa `./dev.sh` en una máquina nueva, instala solo
las dependencias del frontend si hacen falta y crea los `.env` a partir
de los `.env.example` — no hay que acordarse de esos pasos a mano.

---

## Referencia manual (por si `./dev.sh` falla y hay que diagnosticar a mano)

Todo lo de acá abajo es lo que `./dev.sh` hace automáticamente. Sirve
para entender qué está pasando si algo no arranca, o para correr backend
y frontend por separado.

## Backend

### 1. Levantar Postgres (WSL no lo arranca solo)
```bash
service postgresql start
```

### 2. Activar el entorno virtual
```bash
cd /mnt/c/Users/bosch/Desktop/srd-crm/saniflow/saniflow/backend
source .venv/bin/activate
```
Confirmá que el prompt te queda con `(.venv)` adelante.

### 3. Levantar el servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0
```
Abrir: `http://localhost:8000/docs`

Cortar con `Ctrl+C` cuando termines.

## Frontend

En una **segunda terminal**, con el backend ya corriendo en la primera:

```bash
cd /mnt/c/Users/bosch/Desktop/srd-crm/saniflow/saniflow/frontend
npm run dev
```
Abrir: `http://localhost:5173`

Cortar con `Ctrl+C` cuando termines. No hace falta activar ningún venv acá,
eso es solo cosa de Python/backend.

## Rutina de git al final de cada sesión
```bash
cd /mnt/c/Users/bosch/Desktop/srd-crm/saniflow/saniflow    # raíz del proyecto
git status              # revisar qué cambió (chequear que no aparezca .env)
git add .
git commit -m "descripción corta de lo que se hizo"
git push
```

---

## Comandos que se usan menos seguido, pero conviene tener a mano

### Backend

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

### Frontend

**Instalar dependencias** (solo hace falta la primera vez, o si se agregó
alguna librería nueva al `package.json`):
```bash
cd frontend
npm install
```

**Build de producción** (antes de subir a un hosting, o para chequear que
no quedó ningún error de tipos suelto):
```bash
npm run build
```

### Red / WSL

**Si WSL se reinició y `localhost:8000` o `localhost:5173` no conectan
desde el navegador de Windows**:
```bash
hostname -I     # usar esa IP en vez de localhost
```
