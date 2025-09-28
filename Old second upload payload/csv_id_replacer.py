import csv
import json
import os

# Mapping from CSV column to segment_id JSON file
column_to_json = {
    'bo text': 'root_bo_segment_id.json',
    'en text': 'root_en_segment_id.json',
    'zh text': 'root_zh_segment_id.json',
    'bo commentary 1 ': 'commentary_1_bo_segment_id.json',
    'en commentary 1 ': 'commentary_1_en_segment_id.json',
    'lzh commentary 1 ': 'commentary_1_zh_segment_id.json',
    'bo Commentary 2': 'commentary_2_bo_segment_id.json',
    'en commentary 2': 'commentary_2_en_segment_id.json',
    'lzh commentary 2': 'commentary_2_zh_segment_id.json',
}

# Build mapping: for each column, map text -> segment_id
text_to_id = {}
for col, json_file in column_to_json.items():
    if not os.path.exists(json_file):
        print(f'Warning: Mapping file {json_file} for column "{col}" not found!')
        text_to_id[col] = {}
        continue
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
        # Each file has a "segments" list of dicts with 'content' and 'id'
        mapping = {}
        for seg in data.get('segments', []):
            mapping[seg['content'].strip()] = seg['id']
        text_to_id[col] = mapping

input_csv = 'dolma.csv'
output_csv = 'dolma_segment_ids_replaced.csv'

with open(input_csv, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    input_rows = list(reader)

output_rows = [header]
for row_idx, row in enumerate(input_rows):
    new_row = []
    for col, cell in zip(header, row):
        mapping = text_to_id.get(col)
        if mapping is None:
            new_row.append(cell)
            continue
        seg_id = mapping.get(cell.strip())
        if not seg_id:
            print(f'No segment_id found for row {row_idx+2}, column "{col}", text: {cell[:30]}...')
            new_row.append(cell)
        else:
            new_row.append(seg_id)
    output_rows.append(new_row)

with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(output_rows)

print(f'Done. Output written to {output_csv}')
