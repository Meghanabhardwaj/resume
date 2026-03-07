#!/usr/bin/env bash
set -euo pipefail

cd /app

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

if [ ! -d .venv ]; then
  uv sync --frozen
fi

if ! docker image inspect latex-builder >/dev/null 2>&1; then
  echo "Building latex-builder image..."
  docker build -t latex-builder .docker
fi

exec uv run python app.py
