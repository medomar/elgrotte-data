@echo off
REM ===========================
REM ELGROTTE - Configuration
REM Modifier le chemin du disque externe ici
REM ===========================

REM Lettre du disque externe + dossier admin
set SOURCE_DRIVE=E:\Admin

REM Mapping: quel dossier du disque va ou dans le depot
REM Comptabilite -> data/
set SOURCE_DATA=%SOURCE_DRIVE%
REM Tickets/factures -> media/receipts/
set SOURCE_RECEIPTS=%SOURCE_DRIVE%\Tickets
REM Photos/documents -> media/photos/
set SOURCE_PHOTOS=%SOURCE_DRIVE%\Photos
REM Base de donnees -> database/
set SOURCE_DB=%SOURCE_DRIVE%\Database
