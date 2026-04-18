@echo off
REM ============================================================================
REM Security Command Center - uninstaller (Windows).
REM Removes all 15 sibling tool folders, SQLite DB, cached bytecode, and venvs.
REM Nothing was ever installed system-wide, so this is literally delete the folders.
REM ============================================================================

setlocal
cd /d "%~dp0"

echo.
echo ===============================================================
echo   Security Command Center - Uninstaller (Windows)
echo ===============================================================
echo This will DELETE the following from %cd%\..\:
echo   - All 15 sibling security-tool folders
echo   - Local databases (scc.db)
echo   - Cached Python bytecode and virtual environments
echo.
echo Your own files are NOT touched.
echo.
set /p CONFIRM=Type YES to continue:
if /I not "%CONFIRM%"=="YES" (
  echo Aborted.
  pause
  exit /b 0
)

set "PARENT=%~dp0.."
set "REPOS=ai-sast-scanner cloud-misconfig-hunter prompt-injection-proxy compliance-gap-analyzer waf-bypass-lab ai-governance-framework saas-security-posture itdr-engine personal-firewall iam-least-privilege-analyzer k8s-admission-controller cicd-security-scanner mitre-attack-detection-rules soc2-compliance-automation secrets-detection-rotation-engine"

for %%R in (%REPOS%) do (
  if exist "%PARENT%\%%R" (
    echo [*] Removing %%R
    rmdir /s /q "%PARENT%\%%R"
  )
)

REM Clean Command Center local state
if exist "%~dp0data" rmdir /s /q "%~dp0data"
if exist "%~dp0.venv" rmdir /s /q "%~dp0.venv"
if exist "%~dp0__pycache__" rmdir /s /q "%~dp0__pycache__"

echo.
echo [+] Uninstall complete.
echo     The Security Command Center folder itself was kept in case you want
echo     to run start-here.bat again. Delete it manually if you're done.
echo.
pause
