# SaniFlow — Frontend

Interfaz web para el backend de SaniFlow. Stack: **React + TypeScript + Vite
+ Tailwind CSS v4 + TanStack Query + React Router + Recharts**.

## Puesta en marcha local

Requiere el backend corriendo (ver `../backend/README.md`) antes de arrancar,
o vas a ver las pantallas vacías con errores de conexión en la consola.

```bash
cd frontend
npm install
cp .env.example .env    # apunta a http://localhost:8000 por defecto
npm run dev
```

Abrir `http://localhost:5173`.

Si estás en WSL y accedés desde el navegador de Windows y no conecta,
mirá `../docs/COMANDOS_DIARIOS.md` — mismo tema que con el backend.

## Build de producción

```bash
npm run build
```
Genera `dist/`, listo para servir estático (Nginx, Vercel, Netlify, etc.).
Antes de cada build corre chequeo de tipos (`tsc -b`) — si hay un error de
tipos, el build falla ahí, no llega a producción con el bug.

## Estructura

```
src/
├── api/        funciones que llaman al backend, una por entidad
├── types/      tipos TypeScript espejados de los schemas Pydantic
├── components/ piezas reutilizables (Layout, Modal, Kpi, ServiceTag...)
├── pages/      una por pantalla (Pendientes, Realizados, Clientes...)
└── lib/        utilidades (formato de fecha, moneda, etc.)
```

Mismo criterio de capas que el backend: las páginas no arman URLs a mano
ni parsean JSON directo, llaman a `api/*.ts`; si el backend cambia una
ruta, se actualiza en un solo lugar.

## Notas de mantenimiento

- **Los tipos en `src/types/index.ts` son un espejo manual** de
  `backend/app/schemas/*.py`. Si se agrega un campo en un schema de
  Pydantic y no se refleja acá, TypeScript no va a avisar solo — hay que
  acordarse de actualizarlo a mano. (Más adelante se puede automatizar
  generando los tipos desde el `openapi.json` que expone FastAPI en
  `/openapi.json`, pero no hace falta para el tamaño actual del proyecto.)
- El estado del servidor (trabajos, clientes, etc.) vive en **TanStack
  Query**, no en `useState` a mano — por eso al completar un trabajo o
  crear un cliente, las demás pantallas que muestran esos datos se
  actualizan solas (`invalidateQueries`).
