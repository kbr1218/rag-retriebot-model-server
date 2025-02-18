# make_result.py
from functions.convert_to_json import convert_to_json
from functions.convert_to_json import parse_page_content
import json

# 클라이언트에게 전송할 수 있도록 JSON 형식으로 변환 -> db2
def make_result(raw_results):
  print(f">>>>>>>>> make_result 함수 실행")
  results = {
      str(index + 1): {
          **convert_to_json(json.loads(parse_page_content(movie_data["page_content"]))),
          **{
              key: movie_data.get("metadata", {}).get(key, None)  # meta_data가 없을 경우 대비
              for key in ["asset_id", "adult", "runtime", "release_year", "release_month", "release_day", "orgnl_cntry",
                          "original_language", "vote_average", "vote_count", "popularity", "poster_path", "backdrop_path"]
              if key in movie_data["metadata"]                     # key가 존재할 경우만 추가
            }
      }
      for index, (_, movie_data) in enumerate(raw_results["movie_details"].items())
  }
  return results