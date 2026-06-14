@echo off
REM ============================================================
REM  Start Kummo locally (Windows) - just double-click.
REM  Starts a small web server and opens the browser.
REM  Close this window to stop it.
REM  (User-facing messages below are in German on purpose.)
REM ============================================================
setlocal
cd /d "%~dp0"
set "PORT=5500"
set "URL=http://localhost:%PORT%/index.html"
set "SERVER="

REM Look for an available program to start the server.
python --version >nul 2>&1 && set "SERVER=python -m http.server %PORT%"
if not defined SERVER py --version >nul 2>&1 && set "SERVER=py -m http.server %PORT%"
if not defined SERVER where npx >nul 2>&1 && set "SERVER=npx --yes serve -l %PORT% ."

if not defined SERVER (
  echo.
  echo Es wurde weder Python noch Node.js gefunden.
  echo Bitte installieren Sie Python: https://www.python.org/downloads/
  echo ^(Beim Installieren "Add Python to PATH" anhaken.^)
  echo.
  pause
  exit /b 1
)

echo Kummo wird gestartet ...
start "" /b %SERVER%

REM Wait briefly so the server is ready, then open the browser.
timeout /t 2 /nobreak >nul
start "" "%URL%"

echo.
echo Kummo laeuft auf %URL%
echo Zum Beenden dieses Fenster schliessen.
echo.
pause >nul
