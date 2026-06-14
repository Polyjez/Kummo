@echo off
REM ============================================================
REM  Kummo lokal starten (Windows) - einfach doppelklicken.
REM  Startet einen kleinen Webserver und oeffnet den Browser.
REM  Zum Beenden dieses Fenster schliessen.
REM ============================================================
setlocal
cd /d "%~dp0"
set "PORT=5500"
set "URL=http://localhost:%PORT%/index.html"
set "SERVER="

REM Verfuegbares Programm zum Starten des Servers suchen.
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

REM Kurz warten, damit der Server bereit ist, dann Browser oeffnen.
timeout /t 2 /nobreak >nul
start "" "%URL%"

echo.
echo Kummo laeuft auf %URL%
echo Zum Beenden dieses Fenster schliessen.
echo.
pause >nul
