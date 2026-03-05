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
├── scripts/         ← Backup automation scripts
├── .gitattributes   ← Git LFS tracking rules
├── .gitignore       ← Excluded files
└── README.md        ← This file
```

## How It Works

1. The comptable works normally (Excel / accounting software)
2. Files are exported to the `data/` folder
3. At end of day: double-click `scripts/EndOfDay_Backup.bat`
4. Data is automatically versioned and pushed to GitHub

## Machines

| Machine | Role | Permission |
|---------|------|------------|
| Comptable PC | Write data | Push |
| AI machines | Analyze data | Pull only |

## Requirements

- Git installed on comptable PC
- Git LFS installed (`git lfs install`)
- GitHub access configured (SSH key or credential manager)
