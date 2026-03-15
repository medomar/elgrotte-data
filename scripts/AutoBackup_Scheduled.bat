@echo off
REM ===========================
REM ELGROTTE - Sauvegarde Automatique
REM Executee par le Planificateur de taches Windows
REM Ne pas executer manuellement
REM ===========================

set REPO_PATH=%~dp0..
cd /d "%REPO_PATH%"

REM Load config
call "%~dp0sync-config.bat"

REM Log file
set LOGFILE=%REPO_PATH%\scripts\backup.log

echo. >> "%LOGFILE%"
echo =============================== >> "%LOGFILE%"
echo Sauvegarde auto: %date% %time% >> "%LOGFILE%"
echo =============================== >> "%LOGFILE%"

REM Check git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Git non trouve >> "%LOGFILE%"
    exit /b 1
)

REM Sync from external drive (silent)
if exist "%SOURCE_DRIVE%" (
    if exist "%SOURCE_DATA%" (
        robocopy "%SOURCE_DATA%" "data" *.xlsx *.xls *.xlsm *.csv /S /XO /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1
    )
    if exist "%SOURCE_RECEIPTS%" (
        robocopy "%SOURCE_RECEIPTS%" "media\receipts" *.jpg *.jpeg *.png *.pdf /S /XO /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1
    )
    if exist "%SOURCE_PHOTOS%" (
        robocopy "%SOURCE_PHOTOS%" "media\photos" *.jpg *.jpeg *.png *.pdf /S /XO /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1
    )
    if exist "%SOURCE_DB%" (
        robocopy "%SOURCE_DB%" "database" *.db *.sql *.bak /S /XO /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1
    )
    echo [OK] Copie disque externe >> "%LOGFILE%"
) else (
    echo [INFO] Disque externe non present - sauvegarde fichiers locaux uniquement >> "%LOGFILE%"
)

REM Git operations — use comptable branch
git checkout comptable >> "%LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    git checkout -b comptable >> "%LOGFILE%" 2>&1
)

git pull origin comptable --rebase >> "%LOGFILE%" 2>&1
git add data/ database/ media/

git diff --cached --quiet
if %errorlevel% equ 0 (
    echo [INFO] Aucune modification >> "%LOGFILE%"
    exit /b 0
)

for /f "tokens=1-3 delims=/" %%a in ('date /t') do set TODAY=%%a/%%b/%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set NOW=%%a:%%b

git commit -m "Sauvegarde auto ELGROTTE - %TODAY% %NOW%" >> "%LOGFILE%" 2>&1

if %errorlevel% neq 0 (
    echo [ERREUR] Commit echoue >> "%LOGFILE%"
    exit /b 1
)

git push -u origin comptable >> "%LOGFILE%" 2>&1

if %errorlevel% equ 0 (
    echo [OK] Sauvegarde envoyee >> "%LOGFILE%"
) else (
    echo [ATTENTION] Push echoue - sera envoye au prochain essai >> "%LOGFILE%"
)

exit /b 0
