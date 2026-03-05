@echo off
REM ===========================
REM ELGROTTE - Sauvegarde Automatique
REM Executee par le Planificateur de taches Windows
REM Ne pas executer manuellement
REM ===========================

REM Set the repo path (CHANGE THIS to match the comptable's machine)
set REPO_PATH=%~dp0..

cd /d "%REPO_PATH%"

REM Log file for troubleshooting
set LOGFILE=%REPO_PATH%\scripts\backup.log

echo. >> "%LOGFILE%"
echo =============================== >> "%LOGFILE%"
echo Sauvegarde auto: %date% %time% >> "%LOGFILE%"
echo =============================== >> "%LOGFILE%"

REM Check if git is available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Git non trouve >> "%LOGFILE%"
    exit /b 1
)

REM Pull latest changes first (safety)
git pull --rebase >> "%LOGFILE%" 2>&1

REM Stage all changes
git add -A

REM Check if there are changes to commit
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo [INFO] Aucune modification >> "%LOGFILE%"
    exit /b 0
)

REM Get current date for commit message
for /f "tokens=1-3 delims=/" %%a in ('date /t') do set TODAY=%%a/%%b/%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set NOW=%%a:%%b

REM Commit with timestamp
git commit -m "Sauvegarde auto ELGROTTE - %TODAY% %NOW%" >> "%LOGFILE%" 2>&1

if %errorlevel% neq 0 (
    echo [ERREUR] Commit echoue >> "%LOGFILE%"
    exit /b 1
)

REM Push to GitHub
git push >> "%LOGFILE%" 2>&1

if %errorlevel% equ 0 (
    echo [OK] Sauvegarde envoyee >> "%LOGFILE%"
) else (
    echo [ATTENTION] Push echoue - sera envoye au prochain essai >> "%LOGFILE%"
)

exit /b 0
