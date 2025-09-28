import csv
import re
from pydantic import BaseModel
from typing import List, Optional

from enum import Enum

class SegmentType(Enum):
    SOURCE = "source"
    CONTENT = "content"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"

class Mapping(BaseModel):
    text_id: str
    segments: List[str]

class CreateSegment(BaseModel):
    content: str
    type: SegmentType
    mapping: Optional[List[Mapping]] = []


class CreateSegmentRequest(BaseModel):
    text_id: str
    segments: List[CreateSegment]

# Set COLUMN_INDEX to 1 for Tibetan (bo), 2 for Chinese (zh)
COLUMN_INDEX = 2  # 1 = 'bo text', 2 = 'zh text'

CSV_PATH = "/Users/tenzintsering/Desktop/my-work/Scripts/chinese_choejug_mapping_with_bo_choejug.csv"
BO_ID_CSV_PATH = "/Users/tenzintsering/Desktop/my-work/Scripts/bo_choejug_with_id.csv"

def normalize_tibetan(text):
    return text

def fuzzy_match(short, long):
    # Returns True if at least 50% of short is found in long (character overlap)
    if not short or not long:
        return False
    match_count = sum(1 for c in short if c in long)
    return (match_count / max(len(short), 1)) >= 0.5

TEXT_ID = "275811ae-bb7a-4db6-b7af-feab322274c3"

def print_column():
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        create_segment_request = CreateSegmentRequest(
            text_id=TEXT_ID,
            segments=[]
        )
        reader = csv.reader(csvfile)
        header = next(reader, None)
        if not header or COLUMN_INDEX >= len(header):
            print("Invalid column index or missing header.")
            return
        for row in reader:
            if len(row) <= COLUMN_INDEX:
                continue
            value = row[COLUMN_INDEX].strip()
            if value:
                create_segment_request.segments.append(CreateSegment(
                    content=value,
                    type=SegmentType.SOURCE,
                    mapping=[]
                ))
        import json
        from enum import Enum
        # Convert the create_segment_request to a dict, then write to JSON file
        output_path = "create_segment_request_payload.json"
        def default_encoder(obj):
            if isinstance(obj, Enum):
                return obj.value
            try:
                return str(obj)
            except Exception:
                return None
        # Use model_dump if available (Pydantic v2), else dict()
        try:
            data = create_segment_request.model_dump()
        except AttributeError:
            data = create_segment_request.dict()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=default_encoder)
        print(f"create_segment_request written to {output_path}")
        print(create_segment_request)

def print_tibetan_text_ids():
    # Build a mapping from normalized content to _id from bo_choejug_with_id.csv
    content_to_id = {}
    all_contents = []
    with open(BO_ID_CSV_PATH, newline='', encoding='utf-8') as idfile:
        reader = csv.DictReader(idfile)
        for row in reader:
            content = row.get('content', '').strip()
            _id = row.get('_id', '').strip()
            if content and _id:
                norm_content = normalize_tibetan(content)
                content_to_id[norm_content] = _id
                all_contents.append((norm_content, _id))
    # Read Tibetan text from the main CSV and search for its id
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) <= 1:
                continue
            tibetan = row[1].strip()
            if not tibetan:
                continue
            norm_tibetan = normalize_tibetan(tibetan)
            _id = content_to_id.get(norm_tibetan)
            if _id:
                print(_id)
            else:
                # Fuzzy match: at least 50% of norm_tibetan chars in any content
                found = False
                for content, cid in all_contents:
                    if fuzzy_match(norm_tibetan, content):
                        print(cid)
                        found = True
                        break
                if not found:
                    print(f"NOT FOUND: {tibetan}")

if __name__ == "__main__":
    # print_column()  # Uncomment to use the original column print
    print_tibetan_text_ids()  # Call the new function