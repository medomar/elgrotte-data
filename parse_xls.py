#!/usr/bin/env python3
"""Parse XLS cash register files (BIFF/OLE2 format) to extract sales totals.
No external dependencies -- reads BIFF records directly via struct."""

import struct, os, glob, re

def read_biff_records(filepath):
    """Read BIFF records from an XLS file via OLE2 compound file parsing."""
    with open(filepath, 'rb') as f:
        data = f.read()
    if data[:4] != b'\xd0\xcf\x11\xe0':
        return []
    sector_size = 1 << struct.unpack_from('<H', data, 30)[0]
    first_dir_sector = struct.unpack_from('<I', data, 48)[0]
    difat = []
    for i in range(109):
        sid = struct.unpack_from('<i', data, 76 + i * 4)[0]
        if sid >= 0:
            difat.append(sid)
    fat = []
    for sid in difat:
        offset = 512 + sid * sector_size
        for i in range(sector_size // 4):
            fat.append(struct.unpack_from('<i', data, offset + i * 4)[0])
    def read_chain(start_sid):
        result = b''
        sid = start_sid
        visited = set()
        while sid >= 0 and sid not in visited and sid < len(fat):
            visited.add(sid)
            result += data[512 + sid * sector_size:512 + (sid + 1) * sector_size]
            sid = fat[sid]
        return result
    dir_data = read_chain(first_dir_sector)
    workbook_start = -1
    workbook_size = 0
    for i in range(0, len(dir_data), 128):
        entry = dir_data[i:i+128]
        name_len = struct.unpack_from('<H', entry, 64)[0]
        name = entry[:name_len].decode('utf-16-le', errors='ignore').rstrip('\x00')
        if name.lower() in ('workbook', 'book'):
            workbook_start = struct.unpack_from('<I', entry, 116)[0]
            workbook_size = struct.unpack_from('<I', entry, 120)[0]
            break
    if workbook_start < 0:
        return []
    wb_data = read_chain(workbook_start)[:workbook_size]
    records = []
    pos = 0
    while pos + 4 <= len(wb_data):
        rec_type = struct.unpack_from('<H', wb_data, pos)[0]
        rec_len = struct.unpack_from('<H', wb_data, pos + 2)[0]
        records.append((rec_type, wb_data[pos + 4:pos + 4 + rec_len]))
        pos += 4 + rec_len
    return records

def parse_xls_cells(filepath):
    """Extract cell values from XLS file."""
    records = read_biff_records(filepath)
    sst = []
    cells = {}
    for rec_type, rec_data in records:
        if rec_type == 0x00FC and len(rec_data) >= 8:
            unique_strings = struct.unpack_from('<I', rec_data, 4)[0]
            pos = 8
            while len(sst) < unique_strings and pos < len(rec_data):
                if pos + 3 > len(rec_data): break
                char_count = struct.unpack_from('<H', rec_data, pos)[0]
                flags = rec_data[pos + 2]
                pos += 3
                is_unicode = flags & 0x01
                if flags & 0x08:
                    if pos + 2 > len(rec_data): break
                    rich_runs = struct.unpack_from('<H', rec_data, pos)[0]
                    pos += 2
                else:
                    rich_runs = 0
                if flags & 0x04:
                    if pos + 4 > len(rec_data): break
                    ext_size = struct.unpack_from('<I', rec_data, pos)[0]
                    pos += 4
                else:
                    ext_size = 0
                byte_len = char_count * (2 if is_unicode else 1)
                if pos + byte_len > len(rec_data):
                    sst.append('')
                    break
                if is_unicode:
                    s = rec_data[pos:pos + byte_len].decode('utf-16-le', errors='replace')
                else:
                    s = rec_data[pos:pos + byte_len].decode('latin-1', errors='replace')
                pos += byte_len + rich_runs * 4 + ext_size
                sst.append(s)
    for rec_type, rec_data in records:
        if rec_type == 0x00FD and len(rec_data) >= 10:
            row, col = struct.unpack_from('<HH', rec_data, 0)
            idx = struct.unpack_from('<I', rec_data, 6)[0]
            if idx < len(sst):
                cells[(row, col)] = sst[idx]
        elif rec_type == 0x0203 and len(rec_data) >= 14:
            row, col = struct.unpack_from('<HH', rec_data, 0)
            cells[(row, col)] = struct.unpack_from('<d', rec_data, 6)[0]
        elif rec_type == 0x027E and len(rec_data) >= 10:
            row, col = struct.unpack_from('<HH', rec_data, 0)
            rk_raw = struct.unpack_from('<I', rec_data, 6)[0]
            if rk_raw & 0x02:
                val = (rk_raw >> 2)
                if rk_raw & 0x80000000: val -= (1 << 30)
            else:
                val = struct.unpack('<d', struct.pack('<Q', (rk_raw & 0xFFFFFFFC) << 32))[0]
            if rk_raw & 0x01: val /= 100.0
            cells[(row, col)] = val
    return cells

def find_totals(cells):
    """Find summary totals by scanning for known labels."""
    totals = {}
    for (row, col), val in cells.items():
        if not isinstance(val, str):
            continue
        vl = val.strip().lower()
        for key in ['total journ\xe9e :', 'total journ\xe9e net :',
                     'total  r\xe9ductions', 'total remises', 'total tickets offerts',
                     'total charges :', 'total annulations :']:
            if key in vl:
                for c2 in range(15):
                    v = cells.get((row, c2))
                    if isinstance(v, (int, float)):
                        totals[val.strip()] = v
                        break
                break
    return totals

def extract_date_from_filename(filename):
    m = re.search(r'(\d{2})-(\d{2})', filename)
    return f"{m.group(1)}-{m.group(2)}" if m else "unknown"

# ── Main ──
files = sorted(glob.glob('data/*.xls') + glob.glob('data/El grotte 06/*.xls'))
print(f'Found {len(files)} XLS cash register files\n')

results = []
errors = []
seen = {}  # track by (date, total) to flag duplicates

for f in files:
    name = os.path.basename(f)
    folder = os.path.basename(os.path.dirname(f))
    date = extract_date_from_filename(name)
    try:
        cells = parse_xls_cells(f)
        totals = find_totals(cells)
        day_total = day_net = 0
        for k, v in totals.items():
            kl = k.lower()
            if 'net' in kl:
                day_net = v
            elif 'journ' in kl and 'net' not in kl:
                day_total = v
        dup_key = (date, day_total)
        is_dup = dup_key in seen
        if is_dup:
            dup_source = seen[dup_key]
        else:
            seen[dup_key] = f"{folder}/{name}"
        results.append({'file': name, 'folder': folder, 'path': f, 'date': date,
                        'totals': totals, 'day_total': day_total, 'day_net': day_net,
                        'is_dup': is_dup})
    except Exception as e:
        errors.append((name, str(e)))

# Separate unique vs duplicate
unique = [r for r in results if not r['is_dup']]
dupes = [r for r in results if r['is_dup']]

grand_total = sum(r['day_total'] for r in unique)
grand_total_net = sum(r['day_net'] for r in unique)

print(f"{'Date':<12} {'File':<45} {'Total brut':>12} {'Total net':>12}")
print('=' * 83)

for r in sorted(unique, key=lambda x: x['date']):
    dt = f"{r['day_total']:,.1f}" if r['day_total'] else '-'
    dn = f"{r['day_net']:,.1f}" if r['day_net'] else '-'
    src = f" [{r['folder']}]" if r['folder'] != 'data' else ''
    print(f"{r['date']:<12} {r['file']:<45} {dt:>12} {dn:>12}{src}")

print('=' * 83)
print(f"{'GRAND TOTAL (unique days)':<57} {grand_total:>12,.1f} {grand_total_net:>12,.1f}")

dates = sorted(set(r['date'] for r in unique))
print(f"\nDates covered ({len(dates)}): {', '.join(dates)}")
print(f"Files: {len(results)} total, {len(unique)} unique, {len(dupes)} duplicates")

if dupes:
    print(f"\nDuplicate files skipped ({len(dupes)}):")
    for r in dupes:
        print(f"  {r['folder']}/{r['file']} (same as existing {r['date']})")

if errors:
    print(f"\nErrors ({len(errors)}):")
    for name, err in errors:
        print(f"  {name}: {err}")

# Sample breakdown
sample = next((r for r in unique if r['totals']), None)
if sample:
    print(f"\n--- Sample breakdown: {sample['file']} ---")
    for label, val in sample['totals'].items():
        print(f"  {label} {val:,.2f}")
