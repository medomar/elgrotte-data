@echo off
REM ===========================
REM ELGROTTE - Installer la sauvegarde automatique
REM Executez ce script UNE SEULE FOIS en tant qu'administrateur
REM Cree une tache planifiee a 18:00 chaque jour
REM ===========================

echo.
echo ========================================
echo    ELGROTTE - Installation Sauvegarde Auto
echo ========================================
echo.

REM Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Ce script doit etre execute en tant qu'administrateur.
    echo Clic droit ^> Executer en tant qu'administrateur
    echo.
    pause
    exit /b 1
)

REM Get the full path to the auto backup script
set SCRIPT_PATH=%~dp0AutoBackup_Scheduled.bat

REM Delete existing task if present
schtasks /delete /tn "ELGROTTE_AutoBackup" /f >nul 2>&1

REM Create scheduled task at 18:00 every day
schtasks /create /tn "ELGROTTE_AutoBackup" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 04:00 /rl HIGHEST /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    INSTALLATION TERMINEE
    echo ========================================
    echo.
    echo La sauvegarde automatique est programmee
    echo tous les jours a 04h00.
    echo.
    echo Pour modifier l'heure:
    echo   Panneau de configuration ^> Outils d'administration
    echo   ^> Planificateur de taches ^> ELGROTTE_AutoBackup
) else (
    echo.
    echo [ERREUR] L'installation a echoue.
    echo Contactez l'administrateur.
)

echo.
pause
