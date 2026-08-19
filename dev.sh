#!/usr/bin/env bash
# Levanta todo el entorno de desarrollo de SaniFlow de una: Postgres, backend
# y frontend. Correr desde la raíz del proyecto: ./dev.sh
#
# Ctrl+C corta los dos servidores juntos.

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
BACKEND_LOG="/tmp/saniflow-backend.log"
FRONTEND_LOG="/tmp/saniflow-frontend.log"

echo "==> Levantando PostgreSQL..."
service postgresql start > /dev/null

echo "==> Verificando que no haya procesos colgados de una sesión anterior..."
pkill -9 -f "uvicorn app.main:app" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
pkill -9 -f "node.*vite" 2>/dev/null || true
sleep 1

if [ ! -d "$BACKEND/.venv" ]; then
  echo "No encontré $BACKEND/.venv — hace falta crear el entorno virtual del"
  echo "backend una vez a mano (ver backend/README.md) antes de usar este script."
  exit 1
fi

if [ ! -f "$BACKEND/.env" ]; then
  cp "$BACKEND/.env.example" "$BACKEND/.env"
  echo "==> Creé backend/.env a partir de .env.example"
fi

if [ ! -d "$FRONTEND/node_modules" ]; then
  echo "==> Instalando dependencias del frontend (primera vez, puede tardar)..."
  (cd "$FRONTEND" && npm install)
fi

if [ ! -f "$FRONTEND/.env" ]; then
  cp "$FRONTEND/.env.example" "$FRONTEND/.env"
  echo "==> Creé frontend/.env a partir de .env.example"
fi

echo "==> Levantando backend..."
(
  cd "$BACKEND"
  source .venv/bin/activate
  exec uvicorn app.main:app --reload --host 0.0.0.0
) > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

echo "==> Levantando frontend..."
(
  cd "$FRONTEND"
  exec npm run dev -- --host 0.0.0.0
) > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

CLEANED_UP=0
cleanup() {
  if [ "$CLEANED_UP" = "1" ]; then
    return
  fi
  CLEANED_UP=1
  echo ""
  echo "==> Cortando backend y frontend..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  sleep 1
  # Red de seguridad: uvicorn --reload y npm run dev pueden dejar procesos
  # hijos que el kill de arriba no siempre alcanza a matar.
  pkill -9 -f "uvicorn app.main:app" 2>/dev/null || true
  pkill -9 -f "vite" 2>/dev/null || true
  echo "Listo."
}
trap cleanup EXIT INT TERM

sleep 2
echo ""
echo "  Backend:  http://localhost:8000/docs"
echo "  Frontend: http://localhost:5173"
echo ""
echo "  Logs en vivo: tail -f $BACKEND_LOG"
echo "                tail -f $FRONTEND_LOG"
echo ""
echo "  Ctrl+C acá corta los dos servidores."
echo ""

wait