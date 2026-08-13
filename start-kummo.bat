@echo off
REM ============================================================
REM  Start Kummo locally (Windows).
REM  Usage: start-kummo.bat [env]
REM    env = local (default) ^| prod ^| any .env.^<name^> file
REM  For "local": starts Supabase (Docker) if not already running,
REM  then starts a web server and opens the browser.
REM  Close this window to stop it.
REM  (User-facing messages below are in English.)
REM ============================================================
setlocal
cd /d "%~dp0"

set "ENV=%~1"
if "%ENV%"=="" set "ENV=local"
set "ENV_FILE=.env.%ENV%"

if not exist "%ENV_FILE%" (
  echo.
  echo Environment file '%ENV_FILE%' not found.
  echo Available environments:
  for %%f in (.env.*) do echo   - %%~nf
  echo.
  pause
  exit /b 1
)

REM Read credentials for the FastAPI backend
set "SUPABASE_URL="
set "SUPABASE_API_KEY="
for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
  if "%%a"=="SUPABASE_URL" set "SUPABASE_URL=%%b"
  if "%%a"=="SUPABASE_API_KEY" set "SUPABASE_API_KEY=%%b"
)

if not defined SUPABASE_URL (
  echo SUPABASE_URL is missing in '%ENV_FILE%'.
  pause
  exit /b 1
)
if not defined SUPABASE_API_KEY (
  echo SUPABASE_API_KEY is missing in '%ENV_FILE%'.
  pause
  exit /b 1
)

echo Environment: %ENV%

REM --- Supabase (local only) ---
if "%ENV%"=="local" (
  REM Stop any existing (possibly unhealthy) Supabase containers first
  pnpm exec supabase stop >nul 2>&1
  echo Starting local Supabase instance ...
  pnpm exec supabase start
)

REM --- FastAPI backend ---
set "PORT=8000"
set "URL=http://localhost:%PORT%"

where uv >nul 2>&1
if errorlevel 1 (
  echo.
  echo uv not found. Install it: https://docs.astral.sh/uv/getting-started/installation/
  echo.
  pause
  exit /b 1
)

echo Starting Kummo ...
if "%ENV%"=="local" (
  start "" /b uv --directory backend run fastapi dev src\kummo\main.py --port %PORT%
) else (
  start "" /b uv --directory backend run fastapi run src\kummo\main.py --port %PORT%
)

REM Wait briefly so the server is ready, then open the browser.
timeout /t 2 /nobreak >nul
start "" "%URL%"

echo.
echo Kummo is running at %URL%
echo Close this window to stop.
echo To stop Supabase: pnpm exec supabase stop (local only)
echo.
pause >nul
