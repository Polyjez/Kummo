#!/usr/bin/env bash
# ============================================================
#  Start Kummo locally (Linux/macOS).
#  Usage: ./start-kummo.sh [env]
#    env = local (default) | prod | any .env.<name> file
#  For "local": starts Supabase (Docker) if not already running,
#  then starts a web server and opens the browser.
#  Stop it with Ctrl+C.
#  (User-facing messages below are in English.)
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

ENV="${1:-local}"
ENV_FILE=".env.${ENV}"

if [ ! -f "$ENV_FILE" ]; then
  echo >&2
  echo "Environment file '${ENV_FILE}' not found." >&2
  echo "Available environments:" >&2
  for f in .env.*; do echo "  - ${f#.env.}" >&2; done
  echo >&2
  exit 1
fi

# Read .env file and generate js/env.js
SUPABASE_URL=$(grep -E '^SUPABASE_URL=' "$ENV_FILE" | cut -d= -f2-)
SUPABASE_ANON_KEY=$(grep -E '^SUPABASE_ANON_KEY=' "$ENV_FILE" | cut -d= -f2-)

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
  echo >&2
  echo "SUPABASE_URL or SUPABASE_ANON_KEY is missing in '${ENV_FILE}'." >&2
  echo >&2
  exit 1
fi

echo "updating js/config.js..." >&2
sed -i "s|supabaseUrl\s*:[^,]*|supabaseUrl: '${SUPABASE_URL}'|; s|supabaseAnonKey\s*:[^,]*|supabaseAnonKey: '${SUPABASE_ANON_KEY}'|" js/config.js

echo "Environment: ${ENV}" >&2

# --- Supabase (local only) ---
STARTED_SUPABASE=false
if [ "$ENV" = "local" ]; then
  # Stop any existing (possibly unhealthy) Supabase containers first
  npx supabase stop 2>/dev/null || true
  echo "Starting local Supabase instance ..." >&2
  npx supabase start
  STARTED_SUPABASE=true
fi

# --- Web server ---
PORT=5500
URL="http://localhost:${PORT}/index.html"

# Look for an available program to start the server.
if command -v python3 >/dev/null 2>&1; then
  SERVER=(python3 -m http.server "$PORT")
elif command -v python >/dev/null 2>&1; then
  SERVER=(python -m http.server "$PORT")
elif command -v npx >/dev/null 2>&1; then
  SERVER=(npx --yes serve -l "$PORT" .)
else
  echo >&2
  echo "Neither Python nor Node.js was found." >&2
  echo "Please install Python: https://www.python.org/downloads/" >&2
  echo >&2
  exit 1
fi

echo "Starting Kummo ..." >&2
"${SERVER[@]}" &
SERVER_PID=$!

# Stop Supabase on exit only if we started it.
cleanup() {
  kill "$SERVER_PID" 2>/dev/null || true
  if [ "$STARTED_SUPABASE" = true ]; then
    echo >&2
    echo "Stopping Supabase ..." >&2
    npx supabase stop 2>/dev/null || true
  fi
}
trap cleanup EXIT

# Wait briefly, then open the browser.
sleep 2
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "$URL" >/dev/null 2>&1 || true
fi

echo >&2
echo "Kummo is running at ${URL}" >&2
echo "Press Ctrl+C to stop." >&2
echo >&2
wait "$SERVER_PID"
