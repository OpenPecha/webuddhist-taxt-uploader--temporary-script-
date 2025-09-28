import csv
from collections import defaultdict

# File paths
mapping_file = "chinese_choejug_mapping_with_bo_choejug.csv"
segment_file = "zh_choejug_segment_with_id.csv"
output_file = "choejug_mapping_with_id.csv"

# Build a lookup for Chinese text -> text content id
zh_to_id = {}
with open(segment_file, newline='', encoding='utf-8') as seg_f:
    reader = csv.DictReader(seg_f)
    for row in reader:
        zh_to_id[row['content']] = row['_id']

with open(mapping_file, newline='', encoding='utf-8') as map_f, \
     open(output_file, 'w', newline='', encoding='utf-8') as out_f:
    reader = csv.reader(map_f)
    writer = csv.writer(out_f)
    for i, row in enumerate(reader, start=1):
        # Replace only the 3rd column (Chinese text) with its id if possible
        if len(row) >= 3:
            zh_text = row[2]
            text_id = zh_to_id.get(zh_text, '')
            if zh_text.strip() and not text_id:
                print(f"[Line {i}] No id found for: {zh_text}")
            row[2] = text_id
        writer.writerow(row)

# --- Check for duplicate IDs in the output file (excluding header and empty cells) ---
seen = defaultdict(list)
with open(output_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip header if present
    for idx, row in enumerate(reader, start=2):
        if len(row) >= 3 and row[2].strip():
            seen[row[2]].append(idx)

duplicates = {k: v for k, v in seen.items() if len(v) > 1}
if duplicates:
    print("Duplicate IDs found:")
    for dup_id, lines in duplicates.items():
        print(f"ID {dup_id} appears on lines: {lines}")
else:
    print("All IDs are unique.")