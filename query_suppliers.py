import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('database/DatabaseExport-1773436868.203604/Pro-Business-App.sqlite')
cursor = conn.cursor()

print("=" * 60)
print("SUPPLIERS RANKED BY TOTAL ORDER VALUE (TTC)")
print("=" * 60)
cursor.execute(
    "SELECT s.ZFULLNAME, s.ZPHONENUMBER, "
    "COUNT(o.Z_PK) as num_orders, "
    "COALESCE(SUM(o.ZPRICETTC), 0) as total_ttc, "
    "s.ZCURRENTBALANCE, s.ZINCOMEAMOUNT, s.ZOUTCOMEAMOUNT, s.Z_PK "
    "FROM ZSUPPLIER s "
    "LEFT JOIN ZORDER o ON o.ZSUPPLIER = s.Z_PK "
    "GROUP BY s.Z_PK "
    "ORDER BY total_ttc DESC"
)
suppliers = cursor.fetchall()
for s in suppliers:
    print(f"\nSupplier: {s[0]}")
    print(f"  Phone: {s[1]}")
    print(f"  Orders: {s[2]}, Total TTC: {s[3]:.2f} DA")
    print(f"  Balance: {s[4]}, Income: {s[5]}, Outcome: {s[6]}")

if suppliers:
    best_pk = suppliers[0][7]
    best_name = suppliers[0][0]

    print("\n" + "=" * 60)
    print(f"PRODUCTS FROM BEST SUPPLIER: {best_name}")
    print("=" * 60)
    cursor.execute(
        "SELECT ol.ZNAME, SUM(ol.ZQUANTITY) as total_qty, "
        "ol.ZUNITNAME, SUM(ol.ZTTCLINEPRICE) as total_price "
        "FROM ZORDERLINE ol "
        "JOIN ZORDER o ON ol.ZORDER = o.Z_PK "
        "WHERE o.ZSUPPLIER = ? "
        "GROUP BY ol.ZNAME "
        "ORDER BY total_price DESC",
        (best_pk,)
    )
    products = cursor.fetchall()
    for p in products:
        unit = p[2] if p[2] else ""
        print(f"  {p[0]}: {p[1]:.1f} {unit} = {p[3]:.2f} DA")

    print("\n" + "=" * 60)
    print(f"PAYMENTS TO {best_name}")
    print("=" * 60)
    cursor.execute(
        "SELECT ZDATEPAID, ZAMOUNT, ZMETHOD, ZNOTES "
        "FROM ZPAYMENT "
        "WHERE ZSUPPLIER = ? "
        "ORDER BY ZDATEPAID",
        (best_pk,)
    )
    payments = cursor.fetchall()
    total_paid = 0
    for p in payments:
        date_str = "N/A"
        if p[0]:
            date_str = (datetime(2001, 1, 1) + timedelta(seconds=p[0])).strftime("%Y-%m-%d")
        method = p[2] if p[2] else "N/A"
        notes = p[3] if p[3] else ""
        print(f"  {date_str} | {p[1]:.2f} DA | Method: {method} {notes}")
        total_paid += p[1] if p[1] else 0
    print(f"\n  TOTAL PAID: {total_paid:.2f} DA")

conn.close()
