@echo off
REM ===========================
REM ELGROTTE - Sauvegarde Manuelle
REM Cliquez sur ce fichier pour sauvegarder
REM ===========================

cd /d "%~dp0.."

echo.
echo ========================================
echo    ELGROTTE - Sauvegarde
echo ========================================
echo.

REM Load config
call "%~dp0sync-config.bat"

REM Check if git is available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Git n'est pas installe sur cette machine.
    echo Contactez l'administrateur.
    pause
    exit /b 1
)

REM ---- STEP 1: Sync from external drive ----
echo [1/3] Copie depuis le disque externe...

if not exist "%SOURCE_DRIVE%" (
    echo.
    echo [ATTENTION] Disque externe non detecte : %SOURCE_DRIVE%
    echo Verifiez que le disque est branche.
    echo.
    echo Voulez-vous continuer sans copie ? (sauvegarde des fichiers deja presents)
    choice /C ON /M "Oui/Non"
    if %errorlevel% equ 2 (
        pause
        exit /b 0
    )
    goto :skip_sync
)

REM Copy accounting files (Excel, CSV) to data/
if exist "%SOURCE_DATA%" (
    robocopy "%SOURCE_DATA%" "data" *.xlsx *.xls *.xlsm *.csv /S /XO /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1
)

REM Copy receipts to media/receipts/
if exist "%SOURCE_RECEIPTS%" (
    robocopy "%SOURCE_RECEIPTS%" "media\receipts" *.jpg *.jpeg *.png *.pdf /S /XO /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1
)

REM Copy photos to media/photos/
if exist "%SOURCE_PHOTOS%" (
    robocopy "%SOURCE_PHOTOS%" "media\photos" *.jpg *.jpeg *.png *.pdf /S /XO /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1
)

REM Copy database exports
if exist "%SOURCE_DB%" (
    robocopy "%SOURCE_DB%" "database" *.db *.sql *.bak /S /XO /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1
)

echo    Copie terminee.

:skip_sync

REM ---- STEP 2: Git commit ----
echo [2/3] Sauvegarde...

REM Switch to comptable branch (create if needed)
git checkout comptable >nul 2>&1
if %errorlevel% neq 0 (
    git checkout -b comptable >nul 2>&1
)

git pull origin comptable --rebase >nul 2>&1
git add data/ database/ media/

git diff --cached --quiet
if %errorlevel% equ 0 (
    echo.
    echo [INFO] Aucune modification detectee.
    echo Rien a sauvegarder.
    echo.
    pause
    exit /b 0
)

for /f "tokens=1-3 delims=/" %%a in ('date /t') do set TODAY=%%a/%%b/%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set NOW=%%a:%%b

git commit -m "Sauvegarde ELGROTTE - %TODAY% %NOW%"

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] La sauvegarde locale a echoue.
    echo Contactez l'administrateur.
    pause
    exit /b 1
)

REM ---- STEP 3: Push to server ----
echo [3/3] Envoi vers le serveur...
git push -u origin comptable

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    SAUVEGARDE TERMINEE
    echo ========================================
    echo.
) else (
    echo.
    echo [ATTENTION] Sauvegarde locale OK mais envoi echoue.
    echo Verifiez internet. La prochaine sauvegarde enverra tout.
)

echo.
pause
