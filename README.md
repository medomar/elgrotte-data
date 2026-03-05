# ELGROTTE - Café Restaurant Data Repository

Versioned data repository for **ELGROTTE** café-restaurant.

## Structure

```
elgrotte-data/
├── data/            ← Accounting exports (CSV, Excel)
├── media/
│   ├── receipts/    ← Receipt photos / scans
│   └── photos/      ← Other documents / images
├── database/        ← Future: database exports
├── scripts/
│   ├── EndOfDay_Backup.bat      ← Manual backup (desktop shortcut)
│   ├── AutoBackup_Scheduled.bat ← Auto backup (runs at 04:00)
│   └── Install_AutoBackup.bat   ← One-time scheduler setup
├── .gitattributes   ← Git LFS tracking rules
├── .gitignore       ← Excluded files
└── README.md        ← This file
```

## How It Works

1. The comptable works normally (Excel / accounting software)
2. Files are exported to the `data/` folder
3. At end of day: double-click `EndOfDay_Backup.bat` on the desktop
4. Auto backup also runs silently at 04:00 every night

## Machines

| Machine | Role | Permission |
|---------|------|------------|
| Comptable PC | Write data | Push |
| AI machines | Analyze data | Pull only |

---

## Installation Guide

### Windows (Comptable PC)

Open **PowerShell as Administrator** and paste everything below:

```powershell
# 1. Install Git
winget install --id Git.Git -e --source winget

# 2. Refresh PATH (close and reopen PowerShell after this)
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 3. Install Git LFS
git lfs install

# 4. Configure Git identity
git config --global user.name "ELGROTTE"
git config --global user.email "elgrotte@cafe.local"

# 5. Clone the repository (change D:\elgrotte-data to your preferred location)
cd D:\
git clone https://github.com/medomar/elgrotte-data.git

# 6. Create desktop shortcut for manual backup
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Sauvegarde ELGROTTE.lnk")
$Shortcut.TargetPath = "D:\elgrotte-data\scripts\EndOfDay_Backup.bat"
$Shortcut.WorkingDirectory = "D:\elgrotte-data"
$Shortcut.Description = "Sauvegarde manuelle ELGROTTE"
$Shortcut.Save()

# 7. Install the auto backup (daily at 04:00)
# Right-click scripts\Install_AutoBackup.bat > Run as Administrator
```

> **Note:** After step 1, you may need to close and reopen PowerShell for `git` to be recognized.

> **GitHub authentication:** The first time you `git push`, Windows will prompt for GitHub credentials. Use a [Personal Access Token](https://github.com/settings/tokens) (classic, with `repo` scope) as the password. Windows Credential Manager will save it.

### macOS (AI Machine)

Open **Terminal** and paste:

```bash
# 1. Install Git (if not already installed)
xcode-select --install

# 2. Install Git LFS
brew install git-lfs
git lfs install

# 3. Clone the repository
cd ~/Desktop
git clone https://github.com/medomar/elgrotte-data.git

# 4. Done — pull latest data anytime with:
cd ~/Desktop/elgrotte-data && git pull
```

### Linux (AI Machine)

Open **Terminal** and paste:

```bash
# 1. Install Git + Git LFS
sudo apt update && sudo apt install -y git git-lfs

# 2. Initialize LFS
git lfs install

# 3. Clone the repository
cd ~/Desktop
git clone https://github.com/medomar/elgrotte-data.git

# 4. Done — pull latest data anytime with:
cd ~/Desktop/elgrotte-data && git pull
```

---

## After Installation (Windows only)

1. Put your accounting exports (`.csv`, `.xlsx`) in the `data/` folder
2. Put receipts/photos in the `media/` folder
3. To save: double-click **"Sauvegarde ELGROTTE"** on the desktop
4. Auto backup runs every night at 04:00 (if PC is on)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `git` not recognized | Close and reopen PowerShell/Terminal |
| Push fails | Check internet connection — local save is kept, next push will include everything |
| "Authentication failed" | Generate a new [Personal Access Token](https://github.com/settings/tokens) with `repo` scope |
| Auto backup not working | Check Task Scheduler > `ELGROTTE_AutoBackup` task exists and PC is on at 04:00 |
