import csv
import json
import os

# Mapping from CSV column headers to JSON files
COLUMN_TO_JSON = {
    'bo text': 'root_bo_segment_id.json',
    'en text': 'root_en_segment_id.json',
    'zh text': 'root_zh_segment_id.json',
    'bo commentary 1': 'commentary_1_bo_segment_id.json',
    'en commentary 1': 'commentary_1_en_segment_id.json',
    'lzh commentary 1': 'commentary_1_zh.segment_id.json',
    'bo Commentary 2': 'commentary_2_bo_segment_id.json',
    'en commentary': 'commentary_2_en_segment_id.json',
    'lzh commentary': 'commentary_2_zh_segment_id.json',
}

# Normalize column names for matching
NORMALIZE = lambda s: s.strip().lower().replace('_', ' ').replace('.', ' ')

# Build a normalized mapping for flexible header matching
NORMALIZED_COLUMN_TO_JSON = {NORMALIZE(k): v for k, v in COLUMN_TO_JSON.items()}

# Load all JSON segment mappings
segment_maps = {}
for json_file in set(NORMALIZED_COLUMN_TO_JSON.values()):
    if not os.path.exists(json_file):
        print(f"Warning: {json_file} does not exist")
        segment_maps[json_file] = {}
        continue
    
    with open(json_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            segments = data.get('segments', [])
            # Map content to id using direct string matching
            content_to_id = {}
            for seg in segments:
                if 'content' in seg and 'id' in seg and seg['content']:
                    content_to_id[seg['content']] = seg['id']
            segment_maps[json_file] = content_to_id
            print(f"Loaded {len(content_to_id)} segments from {json_file}")
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
            segment_maps[json_file] = {}

# Read the CSV and process
not_found = []
with open('dolma.csv', 'r', encoding='utf-8') as infile, open('dolma_segment_ids.csv', 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    headers = next(reader)
    writer.writerow(headers)
    
    # Map each column index to the appropriate JSON file
    col_to_json = []
    for h in headers:
        norm_h = NORMALIZE(h)
        json_file = NORMALIZED_COLUMN_TO_JSON.get(norm_h)
        col_to_json.append(json_file)
        print(f"Column '{h}' -> {json_file}")
    
    for row_num, row in enumerate(reader, start=2):
        new_row = []
        for idx, cell in enumerate(row):
            json_file = col_to_json[idx]
            if not json_file:
                new_row.append(cell)
                continue
            
            if not cell.strip():
                new_row.append('')
                continue
            
            segment_map = segment_maps.get(json_file, {})
            
            # Try exact match first
            seg_id = segment_map.get(cell)
            if seg_id:
                new_row.append(seg_id)
                continue
            
            # Try stripped match
            seg_id = segment_map.get(cell.strip())
            if seg_id:
                new_row.append(seg_id)
                continue
            
            # Not found - debug
            print(f"\nNot found in row {row_num}, column '{headers[idx]}':")
            print(f"CSV cell content: {repr(cell)}")
            print(f"CSV cell stripped: {repr(cell.strip())}")
            print(f"JSON file: {json_file}")
            print(f"Available content keys (first 3): {list(segment_map.keys())[:3]}")
            
            # Check if any content contains this as substring or vice versa
            matches = []
            for content in segment_map.keys():
                if cell.strip() in content or content in cell.strip():
                    matches.append(content)
            if matches:
                print(f"Potential matches found: {matches[:3]}")
            
            new_row.append('')
            not_found.append((headers[idx], cell.strip()))
        writer.writerow(new_row)

# Print not found entries
if not_found:
    print('\nSegment ID not found for the following content:')
    for col, text in not_found:
        print(f'Column: {col} | Text: {text}')
else:
    print('All segment IDs found successfully!')
