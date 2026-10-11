
import re
import sys
import csv

def decode_raw(timings):
    """
    Decodes a raw IR timing sequence into a bit string based on defined tolerances.
    """
    MARK_MIN = 350
    MARK_MAX = 550
    SHORT_SPACE_MIN = 300
    SHORT_SPACE_MAX = 600
    LONG_SPACE_MIN = 1100
    LONG_SPACE_MAX = 1400

    data = timings[2:]
    bits = ""
    for i in range(0, len(data), 2):
        mark = data[i]
        if i + 1 >= len(data):
            continue
        space = data[i+1]
        if not (MARK_MIN <= mark <= MARK_MAX):
            continue
        if SHORT_SPACE_MIN <= space <= SHORT_SPACE_MAX:
            bits += "0"
        elif LONG_SPACE_MIN <= space <= LONG_SPACE_MAX:
            bits += "1"
    return bits

def bits_to_hex(bits):
    """Converts a bit string to a list of hex strings."""
    if not bits:
        return []
    padding = (8 - len(bits) % 8) % 8
    bits = bits + '0' * padding
    hex_list = []
    for i in range(0, len(bits), 8):
        byte_str = bits[i:i+8]
        byte_val = int(byte_str, 2)
        hex_list.append(f"0x{byte_val:02X}")
    return hex_list

def read_dumps_from_file(file_path):
    """Reads captures from a file with 'label: data' format."""
    captures = []
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.rsplit(':', 1)
                if len(parts) < 2:
                    print(f"Warning: Line {line_num+1} in {file_path} is not in 'label: dump' format. Skipping.")
                    continue
                label = parts[0].strip()
                raw_data = parts[1].strip()
                captures.append((label, raw_data))
    except FileNotFoundError:
        print(f"Error: Input file not found at {file_path}")
        sys.exit(1)
    return captures

def main():
    """Main function to decode dumps from a file and write to a CSV."""
    if len(sys.argv) < 3:
        print("Usage: python3 tools/decode_ir.py <input_dump_file> <output_csv_file>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    
    all_captures = read_dumps_from_file(input_file_path)

    print(f"--- Decoding {len(all_captures)} captures from {input_file_path} ---")

    try:
        with open(output_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header without the 'label' column
            header = [f'B{i+1}' for i in range(14)]
            csv_writer.writerow(header)

            for label, raw_capture in all_captures:
                try:
                    timings = [int(t) for t in raw_capture.split()]
                except ValueError:
                    print(f"Warning: Non-numeric data found for label '{label}'. Skipping.")
                    continue
                
                if not (len(timings) > 2 and timings[0] > 3000 and timings[1] > 1500):
                    print(f"Warning: Skipping invalid or short capture for '{label}'.")
                    continue
                
                bit_string = decode_raw(timings)
                hex_payload = bits_to_hex(bit_string)

                # Write data row without the label
                if hex_payload and len(hex_payload) == 14:
                    csv_writer.writerow(hex_payload)
                else:
                    print(f"Warning: Failed to decode or invalid payload length for label '{label}'. Skipping.")

    except IOError as e:
        print(f"Error writing to output file {output_file_path}: {e}")
        sys.exit(1)

    print(f"--- Done. Decoded data written to {output_file_path} ---")

if __name__ == "__main__":
    main()
