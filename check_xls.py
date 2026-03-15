import subprocess, os, glob

xls_files = sorted(glob.glob("data/*.xls") + glob.glob("data/El grotte 06/*.xls"))

print(f"=== Total XLS files: {len(xls_files)} ===\n")

xls_dates = set()
for f in xls_files:
    name = os.path.basename(f)
    print(f"  {name}")
    parts = name.replace("X_Caisse.", "").replace(".xls", "").replace("2xls", "xls")
    date_part = parts.replace("xls", "").strip()
    xls_dates.add(date_part)

print(f"\n=== Unique dates in XLS files ===")
for d in sorted(xls_dates):
    print(f"  {d}")

db = "database/DatabaseExport-1773436868.203604/Pro-Business-App.sqlite"
r = subprocess.run(["sqlite3", db,
    "SELECT DISTINCT strftime('%d-%m', datetime(ZDATECREATED, 'unixepoch', '+31 years')) as jour FROM ZSELLINGORDERSUMMARY ORDER BY jour;"],
    capture_output=True, text=True)
db_dates = set(r.stdout.strip().split("\n")) if r.stdout.strip() else set()

print(f"\n=== Unique dates in DB: {len(db_dates)} ===")
for d in sorted(db_dates):
    print(f"  {d}")

print(f"\n=== XLS dates: {len(xls_dates)} | DB dates: {len(db_dates)} ===")
