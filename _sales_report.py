import sqlite3
from datetime import datetime, timedelta

APPLE_EPOCH = datetime(2001, 1, 1)

def apple_to_date(ts):
    if ts is None:
        return None
    return APPLE_EPOCH + timedelta(seconds=ts)

DB = '/Users/sayadimohamedomar/Desktop/elgrotte-data/database/DatabaseExport-1773436868.203604/Pro-Business-App.sqlite'
conn = sqlite3.connect(DB)
cur = conn.cursor()

print('=' * 60)
print('  ELGROTTE SALES REPORT')
print('=' * 60)

print()
print('--- 1. PURCHASE ORDERS (ZORDER - supplier invoices) ---')
cur.execute("SELECT COUNT(*), SUM(ZPRICETTC), SUM(ZPRICEHTC) FROM ZORDER WHERE ZORDERTYPE='Invoice'")
r = cur.fetchone()
print(f'  Invoice count: {r[0]}')
print(f'  Total TTC (incl. tax): {r[1]:,.2f}')
print(f'  Total HT (excl. tax):  {r[2]:,.2f}')

cur.execute('SELECT MIN(ZDATECREATED), MAX(ZDATECREATED) FROM ZORDER')
r = cur.fetchone()
print(f'  Date range: {apple_to_date(r[0]).strftime("%Y-%m-%d")} to {apple_to_date(r[1]).strftime("%Y-%m-%d")}')

print()
print('--- 2. SELLING ORDER SUMMARIES (daily sales) ---')
cur.execute('SELECT COUNT(*), SUM(ZPRICETTC), SUM(ZPRICEHTC), SUM(ZPRICE) FROM ZSELLINGORDERSUMMARY')
r = cur.fetchone()
print(f'  Summary count: {r[0]}')
print(f'  Total TTC (incl. tax): {r[1]:,.2f}')
print(f'  Total HT (excl. tax):  {r[2]:,.2f}')
print(f'  Total PRICE:           {r[3]:,.2f}')

cur.execute('SELECT MIN(ZDATECREATED), MAX(ZDATECREATED) FROM ZSELLINGORDERSUMMARY')
r = cur.fetchone()
print(f'  Date range: {apple_to_date(r[0]).strftime("%Y-%m-%d")} to {apple_to_date(r[1]).strftime("%Y-%m-%d")}')

print()
print('--- 3. SELLING ORDER LINES (individual product sales) ---')
cur.execute('SELECT COUNT(*), SUM(ZPRICETTCTOTAL), SUM(ZPRICEHTCTOTAL), SUM(ZQUANTITY) FROM ZSELLINGORDERSUMMARYLINE')
r = cur.fetchone()
print(f'  Line items sold:    {r[0]}')
print(f'  Total TTC:          {r[1]:,.2f}')
print(f'  Total HT:           {r[2]:,.2f}')
print(f'  Total quantity:     {r[3]:,.0f}')

print()
print('--- 4. PAYMENTS ---')
cur.execute('SELECT ZMETHOD, COUNT(*), SUM(ZAMOUNT) FROM ZPAYMENT GROUP BY ZMETHOD ORDER BY SUM(ZAMOUNT) DESC')
rows = cur.fetchall()
print(f'  {"Method":<20} {"Count":>6} {"Amount":>12}')
for r in rows:
    method = r[0] if r[0] else '(empty)'
    print(f'  {method:<20} {r[1]:>6} {r[2]:>12,.2f}')
cur.execute('SELECT SUM(ZAMOUNT) FROM ZPAYMENT')
total = cur.fetchone()[0]
print(f'  {"TOTAL":<20} {"":>6} {total:>12,.2f}')

print()
print('--- 5. SALES BY MONTH (selling order summaries) ---')
cur.execute('SELECT ZDATECREATED, ZPRICETTC FROM ZSELLINGORDERSUMMARY WHERE ZDATECREATED IS NOT NULL ORDER BY ZDATECREATED')
monthly = {}
for row in cur.fetchall():
    d = apple_to_date(row[0])
    key = d.strftime('%Y-%m')
    monthly[key] = monthly.get(key, 0) + (row[1] or 0)

print(f'  {"Month":<10} {"Sales TTC":>12}')
for m in sorted(monthly.keys()):
    print(f'  {m:<10} {monthly[m]:>12,.2f}')
print(f'  {"TOTAL":<10} {sum(monthly.values()):>12,.2f}')

print()
print('--- 6. TOP 20 SELLING PRODUCTS ---')
cur.execute('''
    SELECT sl.ZNAME, SUM(sl.ZQUANTITY) as qty, SUM(sl.ZPRICETTCTOTAL) as total
    FROM ZSELLINGORDERSUMMARYLINE sl
    WHERE sl.ZNAME IS NOT NULL
    GROUP BY sl.ZNAME
    ORDER BY total DESC
    LIMIT 20
''')
print(f'  {"Product":<35} {"Qty":>8} {"Total TTC":>12}')
for r in cur.fetchall():
    name = r[0][:35]
    print(f'  {name:<35} {r[1]:>8,.0f} {r[2]:>12,.2f}')

print()
print('--- 7. SALES BY CATEGORY ---')
cur.execute('''
    SELECT sp.ZCATEGORY, SUM(sl.ZQUANTITY), SUM(sl.ZPRICETTCTOTAL)
    FROM ZSELLINGORDERSUMMARYLINE sl
    LEFT JOIN ZSPRODUCT sp ON sl.ZSPRODUCT = sp.Z_PK
    GROUP BY sp.ZCATEGORY
    ORDER BY SUM(sl.ZPRICETTCTOTAL) DESC
''')
print(f'  {"Category":<30} {"Qty":>8} {"Total TTC":>12}')
for r in cur.fetchall():
    cat = r[0] if r[0] else '(uncategorized)'
    print(f'  {cat:<30} {r[1]:>8,.0f} {r[2]:>12,.2f}')

conn.close()
