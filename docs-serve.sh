#!/usr/bin/env bash
# ============================================================
#  Serve the Kummo documentation site locally (developer tool).
#  Run from anywhere:  ./docs-serve.sh
#  Bootstraps a Python venv under Docs/.venv on first run,
#  installs the MkDocs toolchain, then starts a live-reload server.
#  Stop it with Ctrl+C.
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

VENV="Docs/.venv"
REQUIREMENTS="Docs/requirements.txt"
PORT="${1:-8000}"

# Pick a Python interpreter.
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python was not found. Install it: https://www.python.org/downloads/" >&2
  exit 1
fi

# Create the virtual environment and install dependencies on first run.
if [ ! -x "${VENV}/bin/mkdocs" ]; then
  echo "Setting up the documentation toolchain (first run) ..."
  "$PYTHON" -m venv "$VENV"
  "${VENV}/bin/pip" install --upgrade pip >/dev/null
  "${VENV}/bin/pip" install -r "$REQUIREMENTS"
fi

echo "Documentation site: http://localhost:${PORT}/"
echo "Stop with Ctrl+C."
exec "${VENV}/bin/mkdocs" serve --dev-addr "localhost:${PORT}"
