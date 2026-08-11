#!/usr/bin/env bash
# Automatiza la rutina de git de todos los días.
# Uso: ./save.sh "mensaje del commit"

set -e

if [ -z "$1" ]; then
  echo "Uso: ./save.sh \"mensaje del commit\""
  exit 1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "==> Estado actual:"
git status --short

if git diff --cached --quiet && git diff --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "No hay cambios para guardar."
  exit 0
fi

# Chequeo de seguridad: si .env aparece en lo que se va a subir, frenar.
if git status --porcelain | grep -qE "\.env$"; then
  echo ""
  echo "⚠️  Aparece un archivo .env en los cambios. Puede tener contraseñas."
  echo "    Revisá 'git status' antes de seguir. Se cancela por las dudas."
  exit 1
fi

git add .
git commit -m "$1"
git push

echo "==> Listo, subido a GitHub."
