@echo off
REM ============================================================================
REM Security Command Center - one-click launcher for Windows.
REM Double-click this file from File Explorer. Takes ~2 minutes on first run.
REM ============================================================================

setlocal enabledelayedexpansion

title Security Command Center
cd /d "%~dp0"

echo.
echo ===============================================================
echo   Security Command Center - One-click launcher (Windows)
echo ===============================================================
echo.

REM ---- Check Python ----------------------------------------------------------
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo [X] Python is not installed.
    echo     Download from https://www.python.org/downloads/ ^(5 min^).
    echo     On the install screen, tick "Add Python to PATH".
    echo.
    pause
    exit /b 1
  )
  set "PY=python"
) else (
  set "PY=py"
)

for /f "delims=" %%v in ('!PY! --version 2^>^&1') do set "PYVER=%%v"
echo [+] Found: !PYVER!

REM ---- Check Git -------------------------------------------------------------
where git >nul 2>nul
if errorlevel 1 (
  echo [X] Git is not installed.
  echo     Download from https://git-scm.com/downloads ^(2 min, accept defaults^).
  echo.
  pause
  exit /b 1
)
echo [+] Found: git
echo.

REM ---- Bootstrap sibling repos ----------------------------------------------
echo [*] Cloning / updating all 14 sibling security tools...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap.ps1"
if errorlevel 1 (
  echo.
  echo [X] Bootstrap failed. See messages above.
  pause
  exit /b 1
)
echo.

REM ---- Install Python dependencies ------------------------------------------
echo [*] Installing Python dependencies...
!PY! -m pip install --quiet --upgrade pip
!PY! -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo [X] Could not install Python dependencies.
  pause
  exit /b 1
)
echo [+] Dependencies ready.
echo.

REM ---- Launch server + open browser -----------------------------------------
echo [*] Starting dashboard at http://127.0.0.1:5500 ...
echo     Press Ctrl+C in this window to stop the server when done.
echo.
timeout /t 2 >nul
start "" "http://127.0.0.1:5500"
!PY! server.py

endlocal
