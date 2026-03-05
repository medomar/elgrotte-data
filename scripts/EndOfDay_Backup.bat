@echo off
REM ===========================
REM ELGROTTE - Daily Backup Script
REM Double-click this at end of day
REM ===========================

cd /d "%~dp0.."

echo.
echo ========================================
echo    ELGROTTE - Sauvegarde du jour
echo ========================================
echo.

REM Check if git is available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Git n'est pas installe sur cette machine.
    echo Contactez l'administrateur.
    pause
    exit /b 1
)

REM Stage all changes
git add -A

REM Check if there are changes to commit
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo.
    echo [INFO] Aucune modification detectee aujourd'hui.
    echo Rien a sauvegarder.
    echo.
    pause
    exit /b 0
)

REM Get current date for commit message
for /f "tokens=1-3 delims=/" %%a in ('date /t') do set TODAY=%%a/%%b/%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set NOW=%%a:%%b

REM Commit with timestamp
git commit -m "Sauvegarde ELGROTTE - %TODAY% %NOW%"

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] La sauvegarde locale a echoue.
    echo Contactez l'administrateur.
    pause
    exit /b 1
)

REM Push to GitHub
echo.
echo Envoi vers le serveur...
git push

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    SAUVEGARDE TERMINEE AVEC SUCCES
    echo ========================================
    echo.
    echo Les donnees du jour ont ete sauvegardees.
) else (
    echo.
    echo ========================================
    echo    ATTENTION - ECHEC DE L'ENVOI
    echo ========================================
    echo.
    echo La sauvegarde locale est faite mais l'envoi
    echo vers le serveur a echoue.
    echo Verifiez la connexion internet.
    echo La prochaine sauvegarde enverra tout.
)

echo.
pause
