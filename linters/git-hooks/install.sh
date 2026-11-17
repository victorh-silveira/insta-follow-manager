#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install --hook-type pre-commit --hook-type commit-msg
  echo "Hooks pre-commit e commit-msg instalados com sucesso."
else
  echo "Aviso: pre-commit nao encontrado no PATH. Instale com: pip install pre-commit"
  exit 1
fi
