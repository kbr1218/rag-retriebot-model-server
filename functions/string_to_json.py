# string_to_json.py
import json
import re
import numpy as np

def convert_string_to_json(asset_id: str, page_content: str):
    """
    문자열을 JSON (dict) 객체로 변환하는 함수
    Args:
        asset_id (str): 해당 데이터의 asset_id (오류 발생 시 추적 용도임)
        page_content (str): 변환할 문자열 (e.g. fetch_movie_details()에서 반환된 doc.page_content)
    Returns:
        dict: 변환된 JSON 객체
    """
    try:
        if not isinstance(page_content, str) or len(page_content.strip()) == 0:
            print(">>>>>>>>> page_content가 비어 있거나 문자열이 아님 (asset_id: {asset_id})")
            return None
        
        # nan을 null로 변환
        cleaned_string = re.sub(r"\b[nN][aA][nN]\b", "null", page_content)

        # key에 큰따옴표 추가
        cleaned_string = re.sub(r'(?<!http)(?<!https)(?<!ftp)(\b\w+)\s*:', r'"\1":', cleaned_string)

        # 작은 따옴표를 큰 따옴표로 변환
        cleaned_string = re.sub(r"(?<!\w)'(.*?)'(?!\w)", r'"\1"', cleaned_string)

        # 한글 인용부호(`‘`, `’`)를 일반 따옴표(`"`)로 변환
        cleaned_string = re.sub(r"[‘’]", '"', cleaned_string)

        # Python의 True, False, None >> JSON의 true, false, null 변환
        cleaned_string = re.sub(r'(?<=:\s)True\b', "true", cleaned_string)
        cleaned_string = re.sub(r'(?<=:\s)False\b', "false", cleaned_string)
        cleaned_string = re.sub(r'(?<=:\s)None\b', "null", cleaned_string)

        # JSON 변환
        json_data = json.loads(cleaned_string)
        
        # float 값을 int로 변환 (e.g. release_year: 2023.0 >> 2023)
        for key, value in json_data.items():
            if isinstance(value, float) and value.is_integer():
                json_data[key] = int(value)

            if isinstance(value, float) and np.isnan(value):
                json_data[key] = None

        return json_data

    except json.JSONDecodeError as e:
        print(f">>>>>>>>> JSON 변환 오류 ({asset_id}): {e}")
        return None