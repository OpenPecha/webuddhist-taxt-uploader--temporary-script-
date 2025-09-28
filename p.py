import json

with open("/Users/tenzintsering/Desktop/my-work/Scripts/bo_choejug_toc.json", "r", encoding="utf-8") as f:
    bo_data = json.load(f)

with open("/Users/tenzintsering/Desktop/my-work/Scripts/zh_choejug_toc.json", "r", encoding="utf-8") as f:
    zh_data = json.load(f)


# The file is a list with one object
bo_sections = bo_data[0]["sections"]
zh_sections = zh_data[0]["sections"]

bo_segment_ids = []
zh_segment_ids = []

for section in bo_sections:
    for segment in section["segments"]:
        bo_segment_ids.append(segment["segment_id"])

for section in zh_sections:
    for segment in section["segments"]:
        zh_segment_ids.append(segment["segment_id"])

print(len(bo_segment_ids))
print(len(zh_segment_ids))


from typing import List
from pydantic import BaseModel

class MappingsModel(BaseModel):
    parent_text_id: str
    segments: List[str]

class TextMapping(BaseModel):
    text_id: str
    segment_id: str
    mappings: List[MappingsModel]

class TextMappingRequest(BaseModel):
    text_mappings: List[TextMapping]

text_mapping_request = TextMappingRequest(
    text_mappings=[]
)
zh_index = 0
bo_index = 0
while (zh_index < len(zh_segment_ids) and bo_index < len(bo_segment_ids)):
    if bo_segment_ids[bo_index] == "9faaeb98-9688-4378-a728-0054f81b031c":
        print("bo index reached empty zh segment", bo_segment_ids[bo_index])
        bo_index += 1
        print("bo index", bo_index, " id ", bo_segment_ids[bo_index], "zh index", zh_index, " id ", zh_segment_ids[zh_index])
        continue
    elif zh_index == len(zh_segment_ids) - 1:
        print("zh index reached last segment", zh_segment_ids[zh_index])
        print("bo index", bo_index, " id ", bo_segment_ids[bo_index], "zh index", zh_index, " id ", zh_segment_ids[zh_index])
        break
    text_mapping = TextMapping(
        text_id="275811ae-bb7a-4db6-b7af-feab322274c3",
        segment_id=zh_segment_ids[zh_index],
        mappings=[
            MappingsModel(
                parent_text_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
                segments=[
                    bo_segment_ids[bo_index]
                ]
            )
        ]
    )
    zh_index += 1
    bo_index += 1
    text_mapping_request.text_mappings.append(text_mapping)

import json

# Write the text_mapping_request to a JSON file after the loop is done
with open("text_mapping_request_zh_to_bo.json", "w", encoding="utf-8") as f:
    # Use model_dump if available (Pydantic v2), else fallback to dict()
    try:
        data = text_mapping_request.model_dump()
    except AttributeError:
        data = text_mapping_request.dict()
    json.dump(data, f, ensure_ascii=False, indent=2)
