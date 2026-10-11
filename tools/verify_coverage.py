import csv
import sys
from collections import defaultdict

def reverse_bits(val):
    rev = 0
    for i in range(4):
        if (val >> i) & 1:
            rev |= (1 << (3 - i))
    return rev

def verify_file(file_path):
    print(f"--- Verifying {file_path} ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    print(f"Total rows (excluding header): {len(rows)}")

    modes = {'0xC0': 'Cool', '0x80': 'Heat'}
    by_mode = defaultdict(list)
    for r in rows:
        by_mode[r[6]].append(r)

    temp_map = {}
    for t in range(16, 32):
        code = (reverse_bits(31 - t)) << 4
        temp_map[f"0x{code:02X}"] = t

    for mode_hex, mode_name in modes.items():
        mode_rows = by_mode.get(mode_hex, [])
        print(f"\nMode {mode_name} ({mode_hex}): {len(mode_rows)} records")
        if not mode_rows:
            continue

        by_temp = defaultdict(list)
        for r in mode_rows:
            deg = temp_map.get(r[7], f"Unknown({r[7]})")
            by_temp[deg].append(r)

        complete_temps = 0
        for deg in sorted(by_temp.keys(), key=lambda x: int(x) if isinstance(x, int) else 99):
            items = by_temp[deg]
            b9_unique = set(x[8] for x in items)
            if len(b9_unique) == 35:
                complete_temps += 1
            else:
                print(f"  Temp {deg}°C: {len(b9_unique)}/35 combinations")

        print(f"  Complete temperatures: {complete_temps}/16 (from 16°C to 31°C)")

    unique_keys = set(tuple(r[0:12]) for r in rows)
    print(f"\nUnique settings combinations: {len(unique_keys)} / {len(rows)}")
    if len(unique_keys) == len(rows):
        print("Status: 100% deduplicated and clean!")
    else:
        print(f"Warning: {len(rows) - len(unique_keys)} duplicates found.")

if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'dumps/ir_dictionary.csv'
    verify_file(csv_path)
