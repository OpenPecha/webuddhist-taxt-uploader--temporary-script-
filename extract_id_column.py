import csv

input_file = "choejug_mapping_with_id.csv"
output_file = "choejug_number_id_only.csv"

with open(input_file, newline='', encoding='utf-8') as in_f, \
     open(output_file, 'w', newline='', encoding='utf-8') as out_f:
    reader = csv.reader(in_f)
    for row in reader:
        # Only keep empty row if the input row is exactly ',,'
        if len(row) == 3 and all(not cell.strip() for cell in row):
            out_f.write("\n")  # Write an empty line
        elif len(row) >= 3:
            out_f.write(f"{row[0]},{row[2]}\n")
        # All other cases (e.g., short rows) are ignored