# string_to_json.py
import json
import math

def convert_to_json(obj):
    try:
        if isinstance(obj, dict):
            return {key: convert_to_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_json(item) for item in obj]
        elif isinstance(obj, float):
            # Convert NaN, Infinity, -Infinity to None
            return None if math.isnan(obj) or math.isinf(obj) else obj

        return obj

    except json.JSONDecodeError as e:
        print(f">>>>>>>>> JSON 변환 오류: {e}")
        return None