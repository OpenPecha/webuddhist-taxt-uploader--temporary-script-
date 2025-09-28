import csv
from enum import Enum
import json
from uuid import uuid4
csv_file = 'dolma_segment_ids_replaced.csv'

MAX_ROW = 8

from pydantic import BaseModel
from typing import List, Optional

text_id = {
    "1": "85eedd68-d56e-4086-bf0d-fd46cf9d0dfc",
    "2": "f6d18089-518b-4720-b6dc-47c33e2df1df",
    "3": "c64d4e76-94df-403b-aad5-48b79a530099",
    "4": "abda2074-753e-4472-8864-975b1c7da0c0",
    "5": "d227c1eb-68cf-4dca-ba4b-81f4d45bd1b0",
    "6": "bf51227a-18dd-4e4b-9174-fe413ad30159",
    "7": "607a80c5-65ac-4764-a3ca-1290de91987e",
    "8": "a3b5957b-adca-409a-b909-5816d34fb14a",
    "9": "b2a5f75c-6c61-4c7a-a9b9-f311dab33c39"
}

class TextSegment(BaseModel):
    segment_id: str
    segment_number: int

class Section(BaseModel):
    id: str
    title: Optional[str] = None
    section_number: int
    parent_id: Optional[str] = None
    segments: List[TextSegment] = []
    sections: Optional[List["Section"]] = None
    created_date: Optional[str] = None
    updated_date: Optional[str] = None
    published_date: Optional[str] = None

class TableOfContent(BaseModel):
    id: Optional[str] = None
    text_id: str
    sections: List[Section]

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    payload = TableOfContent(
        id=None,
        text_id=text_id["9"],
        sections=[
            Section(
                id=str(uuid4()),
                title="-",
                section_number=1,
                segments=[]
            )
        ]
    )
    position = 1
    for row in reader:
        if row:  # Check if row is not empty
            payload.sections[0].segments.append(TextSegment(
                segment_id=row[8],
                segment_number=position
            ))
            position += 1
            
    with open('toc_commentary_2_zh.json', 'w', encoding='utf-8') as json_file:
        json.dump(payload.model_dump(mode="json"), json_file, indent=2, ensure_ascii=False)

