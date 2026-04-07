#!/bin/bash

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: ./convert.sh <path/to/file.md> [output.pdf]"
  exit 1
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
INPUT_FILE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUTPUT_FILE="${2:-${INPUT_FILE%.*}.pdf}"

pick_python() {
  for candidate in \
    "${SCRIPT_DIR}/.venv/bin/python" \
    "$(command -v python3 2>/dev/null || true)" \
    "$(command -v python 2>/dev/null || true)"
  do
    if [ -n "${candidate}" ] && [ -x "${candidate}" ] && "${candidate}" -c "import pypandoc" >/dev/null 2>&1; then
      echo "${candidate}"
      return 0
    fi
  done

  return 1
}

if ! PYTHON_BIN="$(pick_python)"; then
  echo "Could not find a Python interpreter with pypandoc installed."
  exit 1
fi

cd "${SCRIPT_DIR}"
"${PYTHON_BIN}" -m src.cli "${INPUT_FILE}" -o "${OUTPUT_FILE}"

echo "Saved ${OUTPUT_FILE}"
