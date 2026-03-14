# ELGROTTE - Donnees Cafe-Restaurant

Depot de donnees pour le cafe-restaurant **ELGROTTE**.

## Comment ca marche

Le comptable ne change **rien** a sa facon de travailler :

1. Il travaille normalement sur son **disque dur externe** (Excel, comptabilite, photos...)
2. Les scripts copient automatiquement les fichiers du disque vers ce depot
3. Git sauvegarde et envoie tout vers le serveur
4. **OpenBridge** recupere les donnees et les analyse cote AI

> Le comptable n'a pas besoin de connaitre Git. Il clique sur un raccourci, c'est tout.

## Structure

```
elgrotte-data/
├── data/               ← Exports comptables (CSV, Excel)
├── media/
│   ├── receipts/       ← Tickets de caisse / justificatifs
│   └── photos/         ← Documents / images
├── database/           ← Exports base de donnees
└── scripts/            ← Scripts de synchronisation (ne pas toucher)
```

## Flux de donnees

```
Disque dur externe (comptable)
        |
        |  robocopy (copie automatique)
        v
elgrotte-data/ (ce depot)
        |
        |  git push (automatique)
        v
GitHub (serveur distant)
        |
        |  git pull (automatique)
        v
OpenBridge (analyse AI)
```

## Configuration

Le fichier `scripts/sync-config.bat` definit le chemin du disque externe :

```bat
set SOURCE_DRIVE=E:\Admin
```

> Modifier cette ligne si la lettre du disque change.

## Installation (une seule fois par l'administrateur)

### PC Comptable (Windows)

```powershell
# 1. Installer Git
winget install --id Git.Git -e --source winget

# 2. Fermer et rouvrir PowerShell, puis :
git lfs install
git config --global user.name "ELGROTTE"
git config --global user.email "elgrotte@cafe.local"

# 3. Cloner le depot
cd D:\
git clone https://github.com/medomar/elgrotte-data.git

# 4. Modifier le chemin du disque externe si necessaire
# Editer D:\elgrotte-data\scripts\sync-config.bat

# 5. Creer le raccourci bureau
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Sauvegarde ELGROTTE.lnk")
$Shortcut.TargetPath = "D:\elgrotte-data\scripts\EndOfDay_Backup.bat"
$Shortcut.WorkingDirectory = "D:\elgrotte-data"
$Shortcut.Description = "Sauvegarde ELGROTTE"
$Shortcut.Save()

# 6. Installer la sauvegarde automatique (en tant qu'administrateur)
# Clic droit > Executer en tant qu'administrateur :
# D:\elgrotte-data\scripts\Install_AutoBackup.bat
```

> Premier `git push` : Windows demandera les identifiants GitHub.
> Utiliser un [Personal Access Token](https://github.com/settings/tokens) (scope `repo`).

### Machine AI (macOS)

```bash
brew install git-lfs && git lfs install
cd ~/Desktop && git clone https://github.com/medomar/elgrotte-data.git
```

OpenBridge fait `git pull` automatiquement avant chaque analyse.

## Machines

| Machine | Role | Acces |
|---------|------|-------|
| PC Comptable | Synchronise le disque externe | Push |
| OpenBridge (AI) | Analyse les donnees | Pull |

## Depannage

| Probleme | Solution |
|----------|----------|
| `git` non reconnu | Fermer et rouvrir PowerShell |
| Push echoue | Verifier internet — la sauvegarde locale est conservee |
| Disque non detecte | Verifier la lettre du disque dans `scripts/sync-config.bat` |
| Sauvegarde auto absente | Planificateur de taches > `ELGROTTE_AutoBackup` |
