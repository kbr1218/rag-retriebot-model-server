import json


# ✅ JSON 변환 함수 (Key-Value 안전 분리)
def parse_page_content(page_content):
    json_dict = {}
    # ✅ `:`(콜론) 기준으로 Key-Value 분리 (마침표 `.` 사용 X)
    segments = page_content.split(". ")  # 마침표 다음 공백을 기준으로 분리
    key = None  # 현재 Key 저장
    value_parts = []  # 현재 Value 저장

    for segment in segments:
        if ":" in segment:  # ✅ 새로운 Key-Value 쌍 발견
            if key is not None:  # ✅ 이전 Key에 대해 저장
                json_dict[key] = " ".join(value_parts).strip()

            key, value = segment.split(":", 1)  # `:`을 기준으로 Key-Value 나누기
            key = key.strip()
            value_parts = [value.strip()]  # 새로운 Value 시작

        else:  # ✅ `overview` 같은 긴 문장 처리
            value_parts.append(segment.strip())

    # ✅ 마지막 Key-Value 저장
    if key is not None:
        json_dict[key] = " ".join(value_parts).strip()

    # ✅ 쉼표(`,`)가 포함된 값은 리스트로 변환
    # for k in ["genre", "actors"]:
    #     if k in json_dict and "," in json_dict[k]:
    #         json_dict[k] = [v.strip() for v in json_dict[k].split(",")]
    json_string = json.dumps(json_dict, indent=2, ensure_ascii=False)
    print(f"----------------------여기 파서{page_content}")
    return json_string
