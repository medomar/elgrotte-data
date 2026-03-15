import sqlite3
from datetime import datetime, timedelta

DB = '/Users/sayadimohamedomar/Desktop/elgrotte-data/database/DatabaseExport-1773436868.203604/Pro-Business-App.sqlite'
conn = sqlite3.connect(DB)
c = conn.cursor()

# Top suppliers by total purchases (ZINCOMEAMOUNT = what we bought from them)
print('=== TOP 15 SUPPLIERS BY TOTAL PURCHASES ===\n')
c.execute('''
    SELECT Z_PK, ZFULLNAME, ZINCOMEAMOUNT, ZOUTCOMEAMOUNT,
           ROUND(ZINCOMEAMOUNT - ZOUTCOMEAMOUNT, 2) as BALANCE
    FROM ZSUPPLIER
    WHERE ZISDEACTIVATED = 0
    ORDER BY ZINCOMEAMOUNT DESC
    LIMIT 15
''')
rows = c.fetchall()
header = f'{"ID":<5} {"Supplier":<30} {"Purchases (TND)":<18} {"Payments (TND)":<18} {"Balance (TND)"}'
print(header)
print('-' * 95)
for r in rows:
    name = r[1] if r[1] else 'N/A'
    inc = r[2] if r[2] else 0
    out = r[3] if r[3] else 0
    bal = r[4] if r[4] else 0
    print(f'{r[0]:<5} {name:<30} {inc:<18.2f} {out:<18.2f} {bal:.2f}')

best = rows[0]
best_id = best[0]
best_name = best[1]
print(f'\n{"="*60}')
print(f'  BEST SUPPLIER: {best_name}')
print(f'{"="*60}')
print(f'  Total Purchases: {best[2]:,.2f} TND')
print(f'  Total Payments:  {best[3]:,.2f} TND')
bal = best[4] if best[4] else 0
print(f'  Balance Owed:    {bal:,.2f} TND')

# Products ordered from this supplier
print(f'\n=== PRODUCTS ORDERED FROM {best_name} ===\n')
c.execute('''
    SELECT pp.ZNAME, pp.ZUNITNAME,
           COUNT(ol.Z_PK) as order_count,
           SUM(ol.ZQUANTITY) as total_qty,
           ROUND(SUM(ol.ZTTCLINEPRICE), 2) as total_spent
    FROM ZORDERLINE ol
    JOIN ZORDER o ON ol.ZORDER = o.Z_PK
    JOIN ZPPRODUCT pp ON ol.ZPPRODUCT = pp.Z_PK
    WHERE o.ZSUPPLIER = ?
    GROUP BY pp.Z_PK, pp.ZNAME
    ORDER BY total_spent DESC
''', (best_id,))
products = c.fetchall()
header2 = f'{"#":<4} {"Product":<35} {"Unit":<10} {"Orders":<8} {"Total Qty":<12} {"Total (TND)"}'
print(header2)
print('-' * 85)
for i, p in enumerate(products, 1):
    name = p[0] if p[0] else 'N/A'
    unit = p[1] if p[1] else '-'
    qty = p[3] if p[3] else 0
    spent = p[4] if p[4] else 0
    print(f'{i:<4} {name:<35} {unit:<10} {p[2]:<8} {qty:<12.1f} {spent:,.2f}')
print(f'\nTotal distinct products: {len(products)}')

# Payments to this supplier
print(f'\n=== PAYMENTS TO {best_name} ===\n')
c.execute('''
    SELECT ZAMOUNT, ZDATEPAID, ZMETHOD, ZNOTES
    FROM ZPAYMENT
    WHERE ZSUPPLIER = ?
    ORDER BY ZDATEPAID DESC
''', (best_id,))
payments = c.fetchall()
header3 = f'{"Amount (TND)":<15} {"Date":<15} {"Method":<15} {"Notes"}'
print(header3)
print('-' * 65)
total_paid = 0
for p in payments:
    amount = p[0] if p[0] else 0
    total_paid += amount
    date_str = ''
    if p[1]:
        try:
            date_str = (datetime(2001, 1, 1) + timedelta(seconds=p[1])).strftime('%Y-%m-%d')
        except Exception:
            date_str = str(p[1])
    method = p[2] if p[2] else ''
    note = p[3] if p[3] else ''
    print(f'{amount:<15.2f} {date_str:<15} {method:<15} {note}')

print(f'\nTotal payments: {len(payments)}')
print(f'Total amount paid: {total_paid:,.2f} TND')

# Number of orders
c.execute('SELECT COUNT(*), ROUND(SUM(ZPRICETTC),2) FROM ZORDER WHERE ZSUPPLIER = ?', (best_id,))
order_info = c.fetchone()
print(f'\nTotal purchase orders: {order_info[0]}')
print(f'Total order value: {order_info[1]:,.2f} TND')

conn.close()
