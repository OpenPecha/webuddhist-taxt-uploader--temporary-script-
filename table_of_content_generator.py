from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import csv

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

file_path = "/Users/tenzintsering/Desktop/my-work/Scripts/choejug_number_id_only.csv"

with open(file_path, encoding="utf-8") as f:
    reader = csv.reader(f)
    table_of_content = TableOfContent(
        text_id="275811ae-bb7a-4db6-b7af-feab322274c3",
        sections=[]
    )
    section_number_count = 1
    section = Section(
        id=str(uuid4()),
        section_number=section_number_count,
        title=str(section_number_count),
        segments=[]
    )
    segment_number_count = 1
    for row in reader:
        if len(row) > 0:
            if len(row[1]) > 0:
                segment = TextSegment(
                    segment_id=row[1],
                    segment_number=segment_number_count
                )
                section.segments.append(segment)
                segment_number_count += 1
            else:
                pass
        else:
            table_of_content.sections.append(section)
            section_number_count += 1
            segment_number_count = 1
            section = Section(
                id=str(uuid4()),
                section_number=section_number_count,
                title=str(section_number_count),
                segments=[]
            )
    table_of_content.sections.append(section)
    import json

    output_file = "zh_choejug_table_of_content.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(table_of_content.dict(), json_file, ensure_ascii=False, indent=2)