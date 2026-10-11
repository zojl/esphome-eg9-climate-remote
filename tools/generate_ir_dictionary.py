import csv

def generate_ir_dictionary(dump_file_path):
    ir_dict_entries = []
    with open(dump_file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 14:
                try:
                    full_frame = [int(b, 16) for b in row]
                    key = full_frame[5:12]
                    value = full_frame[12:14]
                    ir_dict_entries.append((key, value))
                except ValueError:
                    # Skip rows that don't contain valid hex
                    pass
    return ir_dict_entries

def format_as_cpp_map(ir_dict_entries):
    cpp_map_string = "const std::map<std::vector<uint8_t>, std::pair<uint8_t, uint8_t>> EG9Climate::IR_CODE_DICTIONARY = {\n"
    for key, value in ir_dict_entries:
        key_str = ", ".join([f"0x{b:02X}" for b in key])
        value_str = f"0x{value[0]:02X}, 0x{value[1]:02X}"
        cpp_map_string += f"    {{ {{ {key_str} }}, {{ {value_str} }} }},\n"
    cpp_map_string += "};"
    return cpp_map_string

def main():
    import sys
    dump_file = sys.argv[1] if len(sys.argv) > 1 else 'dumps/ir_dictionary.csv'
    ir_dict_entries = generate_ir_dictionary(dump_file)
    cpp_map = format_as_cpp_map(ir_dict_entries)
    print(cpp_map)

if __name__ == '__main__':
    main()
