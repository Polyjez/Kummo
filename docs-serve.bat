@echo off
REM ============================================================
REM  Serve the Kummo documentation site locally (developer tool).
REM  Double-click, or run:  docs-serve.bat [port]
REM  Bootstraps a Python venv under Docs\.venv on first run,
REM  installs the MkDocs toolchain, then starts a live-reload server.
REM  Close this window or press Ctrl+C to stop it.
REM ============================================================
setlocal
cd /d "%~dp0"

set "VENV=Docs\.venv"
set "REQUIREMENTS=Docs\requirements.txt"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8000"

REM Pick a Python interpreter.
set "PYTHON="
py --version >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON python --version >nul 2>&1 && set "PYTHON=python"

if not defined PYTHON (
  echo.
  echo Python was not found. Install it: https://www.python.org/downloads/
  echo ^(Tick "Add Python to PATH" during installation.^)
  echo.
  pause
  exit /b 1
)

REM Create the virtual environment and install dependencies on first run.
if not exist "%VENV%\Scripts\mkdocs.exe" (
  echo Setting up the documentation toolchain ^(first run^) ...
  %PYTHON% -m venv "%VENV%"
  "%VENV%\Scripts\python.exe" -m pip install --upgrade pip >nul
  "%VENV%\Scripts\pip.exe" install -r "%REQUIREMENTS%"
)

echo Documentation site: http://localhost:%PORT%/
echo Stop by closing this window or pressing Ctrl+C.
"%VENV%\Scripts\mkdocs.exe" serve --dev-addr "localhost:%PORT%"
