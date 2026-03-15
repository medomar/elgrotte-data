#!/usr/bin/env python3
"""Debug: dump all cells from first XLS file."""

import struct, os, glob

def read_biff_records(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    if data[:4] == b'\xd0\xcf\x11\xe0':
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
                offset = 512 + sid * sector_size
                result += data[offset:offset + sector_size]
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
    else:
        wb_data = data
    records = []
    pos = 0
    while pos + 4 <= len(wb_data):
        rec_type = struct.unpack_from('<H', wb_data, pos)[0]
        rec_len = struct.unpack_from('<H', wb_data, pos + 2)[0]
        rec_data = wb_data[pos + 4:pos + 4 + rec_len]
        records.append((rec_type, rec_data))
        pos += 4 + rec_len
    return records

files = sorted(glob.glob('data/*.xls'))
f = files[0]
print(f"=== Dumping records from {os.path.basename(f)} ===\n")

records = read_biff_records(f)

# Show record types
from collections import Counter
types = Counter(rt for rt, _ in records)
print("Record types found:")
for rt, count in sorted(types.items()):
    print(f"  0x{rt:04X}: {count} records")

# Show SST content
print("\n=== SST strings ===")
for rec_type, rec_data in records:
    if rec_type == 0x00FC:
        if len(rec_data) >= 8:
            total_s = struct.unpack_from('<I', rec_data, 0)[0]
            unique_s = struct.unpack_from('<I', rec_data, 4)[0]
            print(f"Total strings: {total_s}, Unique: {unique_s}")

# Show all NUMBER records
print("\n=== NUMBER records (0x0203) ===")
for rec_type, rec_data in records:
    if rec_type == 0x0203 and len(rec_data) >= 14:
        row = struct.unpack_from('<H', rec_data, 0)[0]
        col = struct.unpack_from('<H', rec_data, 2)[0]
        val = struct.unpack_from('<d', rec_data, 6)[0]
        print(f"  ({row},{col}) = {val}")

# Show all RK records
print("\n=== RK records (0x027E) ===")
for rec_type, rec_data in records:
    if rec_type == 0x027E and len(rec_data) >= 10:
        row = struct.unpack_from('<H', rec_data, 0)[0]
        col = struct.unpack_from('<H', rec_data, 2)[0]
        rk_raw = struct.unpack_from('<I', rec_data, 6)[0]
        print(f"  ({row},{col}) rk_raw=0x{rk_raw:08X}")

# Show LABELSST records
print("\n=== LABELSST records (0x00FD) ===")
for rec_type, rec_data in records:
    if rec_type == 0x00FD and len(rec_data) >= 10:
        row = struct.unpack_from('<H', rec_data, 0)[0]
        col = struct.unpack_from('<H', rec_data, 2)[0]
        sst_idx = struct.unpack_from('<I', rec_data, 6)[0]
        print(f"  ({row},{col}) sst_idx={sst_idx}")

# Show MULRK records (0x00BD)
print("\n=== MULRK records (0x00BD) ===")
for rec_type, rec_data in records:
    if rec_type == 0x00BD:
        row = struct.unpack_from('<H', rec_data, 0)[0]
        first_col = struct.unpack_from('<H', rec_data, 2)[0]
        last_col = struct.unpack_from('<H', rec_data, len(rec_data)-2)[0]
        print(f"  row={row}, cols={first_col}-{last_col}, len={len(rec_data)}")

# Show FORMULA records (0x0006 or 0x0406)
print("\n=== FORMULA records ===")
for rec_type, rec_data in records:
    if rec_type in (0x0006, 0x0406) and len(rec_data) >= 14:
        row = struct.unpack_from('<H', rec_data, 0)[0]
        col = struct.unpack_from('<H', rec_data, 2)[0]
        val = struct.unpack_from('<d', rec_data, 6)[0]
        print(f"  ({row},{col}) = {val}")
