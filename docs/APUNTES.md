# Apuntes de SaniFlow

Bitácora práctica del desarrollo. No es documentación formal del sistema
(para eso están `ARQUITECTURA.md` y `MODELO_DE_DATOS.md`, cuando existan) —
esto es el "por qué hicimos esto así" en el momento en que se decidió,
para poder volver atrás y entender el propio criterio pasado.

Cada entrada es una sesión de trabajo. Se agrega, no se reescribe: si algo
cambia más adelante, se anota como una entrada nueva que dice "esto lo
habíamos hecho así, ahora lo cambiamos por tal motivo" — así queda el
historial de decisiones, no solo el estado final.

---

## Sesión 1 — Armado del backend

### Qué se construyó
Un backend en **FastAPI + PostgreSQL**, con migraciones versionadas
(Alembic), datos de prueba (seed) y tests automatizados. Vive en
`backend/`. Todavía no tiene interfaz visual — se opera vía `/docs`
(Swagger, autogenerado por FastAPI) o `curl`.

### Por qué esta arquitectura en capas
El código de `backend/app/` está separado en:

```
models/     -> las tablas (qué hay guardado)
schemas/    -> qué entra y sale de la API (no siempre es igual al modelo)
crud/       -> leer/escribir en la base, sin decidir nada
services/   -> las reglas del negocio ("completar un trabajo hace X")
api/routers/ -> los endpoints HTTP, finitos: reciben, delegan, devuelven
```

La regla es que cada capa solo conoce a la de abajo:
`routers → services → crud → models`. Un router nunca escribe SQL
directamente, y un service nunca sabe qué es un `Request` de HTTP.

**Por qué importa esto en la práctica:** cuando el sistema crezca (por
ejemplo cuando agreguemos la app para técnicos, o facturación), la lógica
de "qué pasa cuando se completa un trabajo" va a poder reusarse desde
otro lado sin duplicar código, porque no está pegada a un endpoint
específico. Está en `services/trabajos_service.py`, no en
`api/routers/trabajos.py`.

### Conceptos clave usados (glosario práctico)

- **ORM (SQLAlchemy)**: en vez de escribir SQL a mano, se define la tabla
  como una clase de Python (`app/models/cliente.py`) y la librería
  traduce. `Cliente.query...` en vez de `SELECT * FROM clientes`.

- **Migraciones (Alembic)**: cada cambio en el modelo de datos (agregar
  una columna, una tabla) se guarda como un archivo versionado en
  `alembic/versions/`. Esto es lo que separa "cambiar el código" de
  "cambiar la base de datos real" — sin esto, cada vez que se modifica un
  modelo habría que alterar la tabla a mano en producción, con riesgo de
  romper datos existentes. El comando que genera el archivo es
  `alembic revision --autogenerate -m "descripción"`, y el que lo aplica
  es `alembic upgrade head`.

- **Pydantic (schemas)**: valida automáticamente los datos que entran por
  la API (si falta un campo obligatorio, o el tipo está mal, rechaza el
  request antes de que llegue al código de negocio). Por eso
  `ClienteCreate` y `ClienteOut` son clases separadas del modelo de
  base de datos: no siempre queremos exponer o pedir los mismos campos.

- **Dependency injection (`Depends(get_db)`)**: cada request a la API
  recibe su propia sesión de base de datos, que se abre al empezar el
  request y se cierra sola al terminar. Está en `app/core/database.py`.

- **Seed de datos** (`scripts/seed_data.py`): datos ficticios pero
  realistas para poder probar y hacer demos sin depender de cargar todo
  a mano. Se puede correr las veces que haga falta — borra y vuelve a
  crear.

### Decisiones de negocio ya tomadas (y por qué)

- **Completar un trabajo con contrato activo genera solo el próximo.**
  Vive en `services/trabajos_service.py::completar_trabajo`. La lógica:
  si el trabajo que se cierra tiene un `contrato_id` con frecuencia
  definida (mensual, trimestral, etc.), se calcula la fecha del próximo
  servicio y se crea automáticamente en estado "pendiente". Así nadie
  tiene que acordarse de reagendar un cliente con plan fijo.

- **"Cliente en riesgo" es una heurística, no una IA.** Vive en
  `services/clientes_service.py::clientes_en_riesgo`. Hoy detecta dos
  señales: 2+ reclamos en 90 días, o un contrato vencido sin nada
  agendado. Es intencionalmente simple para poder auditar por qué un
  cliente aparece marcado — más adelante se puede sofisticar, pero
  siempre debería quedar claro el motivo (no una caja negra).

- **"Problema recurrente" se arma con etiquetas libres**, no con una
  lista fija de problemas predefinidos. Cualquiera que cierra un trabajo
  o carga un reclamo puede escribir una etiqueta nueva
  (`"reaparición de cucarachas"`, `"acceso difícil"`, etc.), y si esa
  etiqueta aparece 2+ veces en el historial de un cliente, se considera
  recurrente. Ventaja: no hay que anticipar todos los problemas posibles
  de antemano. Desventaja a vigilar: si dos personas escriben la misma
  idea con palabras distintas, no se van a agrupar solas — en algún
  momento puede convenir normalizar a una lista sugerida.

### Cómo se probó (no fue "a ojo")
Antes de entregar el backend se levantó un PostgreSQL real, se corrieron
las migraciones contra esa base, se cargó el seed, y se probó a mano
todo el flujo por `curl`: crear un trabajo con contrato → completarlo →
confirmar que generó el próximo automáticamente. Después se escribieron
tests automatizados (`tests/test_trabajos.py`) que repiten esos mismos
casos contra una base SQLite en memoria, para que cualquier cambio
futuro que rompa este comportamiento se note enseguida corriendo
`pytest tests/ -v`, sin tener que probarlo a mano de nuevo cada vez.

### Pendiente de documentar (deuda reconocida, no urgente)
- `ARQUITECTURA.md`: diagrama y explicación más formal de las capas.
- `MODELO_DE_DATOS.md`: diagrama entidad-relación de las 9 tablas.
- `ROADMAP.md`: las etapas que se charlaron (stock/insumos, cuenta
  corriente, roles de usuario, app para técnicos, facturación
  electrónica) puestas en orden con criterio de cuándo abordar cada una.

---

## Sesión 2 — Frontend

### Qué se construyó
Interfaz en **React + TypeScript + Vite**, en `frontend/`. Reemplaza al
prototipo interactivo del principio (aquel vivía en el chat, con datos
inventados) por pantallas reales conectadas al backend de la Sesión 1.

### Decisión de stack (y qué se descartó)
- **Vite** en vez de Next.js: no hay necesidad de server-side rendering
  ni rutas de backend en el frontend (eso ya lo resuelve FastAPI). Vite
  da un dev server rápido y un build simple para una SPA (single-page
  app) común y corriente.
- **TanStack Query** en vez de guardar los datos del servidor a mano con
  `useState` + `useEffect`: se encarga solo de cachear, revalidar, y —lo
  más importante en la práctica— de que cuando una pantalla cambia un
  dato (ej. completar un trabajo), las otras pantallas que muestran ese
  mismo dato se actualicen sin tener que escribir ese "avisale a los
  demás" a mano. Eso es lo que hace `qc.invalidateQueries(...)` en los
  formularios.
- **Tailwind v4**: cambió bastante respecto a v3 (ya no se usa
  `tailwind.config.js` de la misma forma, ahora los tokens de diseño
  viven en el propio CSS con `@theme`). Se documenta acá porque si se
  busca ayuda en internet, la mayoría de los tutoriales todavía muestran
  la sintaxis vieja de v3 y confunde.

### El punto flojo a vigilar: los tipos están duplicados a mano
`frontend/src/types/index.ts` repite, en TypeScript, la forma de los
schemas de Pydantic del backend (`ClienteOut`, `TrabajoOut`, etc.). Hoy
se mantienen sincronizados a mano. **Esto se va a romper en algún
momento** — alguien va a agregar un campo en el backend, olvidarse de
actualizar el tipo del frontend, y el error va a aparecer recién en
tiempo de ejecución (la propiedad llega `undefined`), no al compilar.
Cuando eso empiece a doler, la solución estándar es generar estos tipos
automáticamente desde `/openapi.json` (FastAPI lo expone solo, sin
código extra) con una herramienta como `openapi-typescript`. No se hizo
ahora porque para 8 entidades no vale la pena la complejidad extra
todavía — pero si el modelo de datos crece bastante, revisar esto.

### Cómo se verificó
No alcanza con que compile: se levantó el backend contra Postgres real
(con los datos del seed de la Sesión 1) y el frontend en paralelo, y se
probó a mano por `curl` que el preflight de CORS responde bien para el
origen `http://localhost:5173` y que el endpoint que usa la pantalla de
Pendientes devuelve los trabajos reales. El chequeo de tipos (`tsc -b`)
y el build de producción (`npm run build`) también se corrieron antes de
entregar el código — encontraron 3 errores reales (tipos de Recharts,
imports sin usar) que se corrigieron ahí mismo.

---

## Sesión 3 — Revisión crítica y correcciones

### Qué se corrigió
Revisión de UX/frontend con ojo crítico (no solo "¿compila?", sino "¿qué
pasa cuando algo sale mal, o cuando alguien toca donde no quería?"). Se
arreglaron 3 cosas:

1. **Las pantallas no distinguían "no hay datos" de "no pude conectarme
   al backend".** Antes, si la API estaba caída, `Pendientes`/`Clientes`/
   `Realizados`/la ficha de cliente mostraban el mismo mensaje que si
   realmente no hubiera nada cargado — lo cual es directamente engañoso
   (parece "no tenés visitas hoy" cuando en realidad el sistema no
   respondió). Se agregó manejo de `isError` en cada pantalla, con un
   componente nuevo `ErrorState` que además ofrece un botón de
   "Reintentar" (`refetch()` de TanStack Query).

2. **Cancelar una visita era de un solo toque, sin vuelta atrás.** Se
   agregó `ConfirmDialog`, un componente genérico de confirmación
   (reutilizable para cualquier acción destructiva futura), y ahora
   cancelar pide confirmar antes de ejecutar la mutación.

3. **Se reemplazó el `alert()` nativo del navegador** (que se usaba para
   avisar que se generó automáticamente el próximo trabajo de un
   contrato) **por un sistema de notificaciones propio** (`Toast.tsx`,
   con contexto de React vía `useToast()`). Queda estilado acorde al
   resto de la app y no bloquea la interacción como sí hace `alert()`.

De paso, se corrigieron dos detalles menores: el título de la pestaña
del navegador (quedó "frontend", el default de Vite) y el `lang="en"`
del HTML (debía ser `"es"`).

### Deuda de UX reconocida, para más adelante (no se tocó todavía)
- Sin favicon propio (sigue el de Vite).
- Estados de carga son texto plano ("Cargando…"), sin esqueleto.
- `Realizados` no tiene filtros ni paginación — con meses de uso real
  esa tabla va a volverse difícil de navegar.
- El Dashboard no compara contra el período anterior (ej. "+12% vs mes
  pasado"), que es el tipo de dato que más ayuda a decidir.
- Contraste de color un poco bajo en textos secundarios (`text-muted`
  sobre blanco, en mayúsculas chiquitas) — revisar accesibilidad si en
  algún momento el dueño lo usa mucho tiempo seguido en el celular.

### Backlog funcional anotado (todavía no diseñado ni implementado)
**Separar los trabajos en "Eventuales" y "Fijos".** Idea: un trabajo
"Fijo" es el que nace de un contrato con frecuencia periódica (los que
ya generan su propio "próximo trabajo" automáticamente al completarse);
un trabajo "Eventual" es el de un cliente que llama una sola vez, sin
contrato detrás (una casa, un comercio puntual). Hoy el modelo de datos
ya distingue esto de forma implícita —`trabajo.contrato_id` es `null` en
los eventuales, y tiene valor en los fijos— pero no está expuesto en la
interfaz como una categoría visible. Cuando se aborde, pensar si
conviene:
(a) simplemente agregar un filtro/tab en `Pendientes` y `Realizados`
    que separe por `contrato_id != null`, sin tocar el modelo de datos, o
(b) sumar un campo explícito `tipo_trabajo` en el backend si con el
    tiempo aparecen reglas de negocio distintas para cada categoría
    (ej. prioridad automática, recordatorios distintos, tarifas base
    diferentes) que no se puedan resolver solo mirando si hay contrato.
La opción (a) es más simple y probablemente alcance al principio.

