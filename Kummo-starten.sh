#!/usr/bin/env bash
# ============================================================
#  Kummo lokal starten (Linux) - im Dateimanager doppelklicken
#  oder im Terminal ausfuehren: ./Kummo-starten.sh
#  Startet einen kleinen Webserver und oeffnet den Browser.
#  Zum Beenden: Strg+C druecken.
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

PORT=5500
URL="http://localhost:${PORT}/index.html"

# Verfuegbares Programm zum Starten des Servers suchen.
if command -v python3 >/dev/null 2>&1; then
  SERVER=(python3 -m http.server "$PORT")
elif command -v python >/dev/null 2>&1; then
  SERVER=(python -m http.server "$PORT")
elif command -v npx >/dev/null 2>&1; then
  SERVER=(npx --yes serve -l "$PORT" .)
else
  echo
  echo "Es wurde weder Python noch Node.js gefunden."
  echo "Bitte installieren Sie Python: https://www.python.org/downloads/"
  echo
  exit 1
fi

echo "Kummo wird gestartet ..."
"${SERVER[@]}" &
SERVER_PID=$!

# Server beim Beenden (Strg+C) sauber stoppen.
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

# Kurz warten, dann Browser oeffnen.
sleep 2
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "$URL" >/dev/null 2>&1 || true
fi

echo
echo "Kummo laeuft auf ${URL}"
echo "Zum Beenden: Strg+C druecken."
echo
wait "$SERVER_PID"
