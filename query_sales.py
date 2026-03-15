import subprocess, sys

db = "database/DatabaseExport-1773436868.203604/Pro-Business-App.sqlite"

queries = {
    "Total ventes": "SELECT COUNT(*) as nb_ventes, ROUND(SUM(ZPRICETTC), 2) as total_ttc FROM ZSELLINGORDERSUMMARY;",
    "Ventes par mois": "SELECT strftime('%Y-%m', datetime(ZDATECREATED, 'unixepoch', '+31 years')) as mois, COUNT(*) as nb, ROUND(SUM(ZPRICETTC), 2) as total FROM ZSELLINGORDERSUMMARY GROUP BY mois ORDER BY mois;",
    "Top 15 produits vendus": "SELECT ZNAME, ROUND(SUM(ZQUANTITY)) as qty, ROUND(SUM(ZPRICETOTAL), 2) as total FROM ZSELLINGORDERSUMMARYLINE GROUP BY ZNAME ORDER BY SUM(ZPRICETOTAL) DESC LIMIT 15;",
    "Ventes par jour (last 30)": "SELECT strftime('%Y-%m-%d', datetime(ZDATECREATED, 'unixepoch', '+31 years')) as jour, COUNT(*) as nb, ROUND(SUM(ZPRICETTC), 2) as total FROM ZSELLINGORDERSUMMARY GROUP BY jour ORDER BY jour DESC LIMIT 30;",
}

for label, q in queries.items():
    print(f"\n=== {label} ===")
    r = subprocess.run(["sqlite3", db, q], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.stderr:
        print("ERR:", r.stderr.strip())
