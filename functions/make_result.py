from functions.convert_to_json import convert_to_json
from functions.page_content_parser import parse_page_content
import json

# 클라이언트에게 전송할 수 있도록 JSON 형식으로 변환 -> db1
def make_result_for_db1(raw_results):
    results = {
      str(index + 1): convert_to_json(json.loads(movie_data["page_content"]))
      for index, (_, movie_data) in enumerate(raw_results["movie_details"].items())
    }
    return results

# 클라이언트에게 전송할 수 있도록 JSON 형식으로 변환 -> db2
def make_result_for_db2(raw_results):
  results = {
      str(index + 1): {
          **convert_to_json(json.loads(parse_page_content(movie_data["page_content"]))),  # ✅ 기존 데이터 변환
          **{
              key: movie_data["meta_data"][key]  # ✅ meta_data에서 특정 key 추가
              for key in ["asset_id", "adult", "runtime", "release_year", "release_month", "release_day", "orgnl_cntry", "original_language", "vote_average", "vote_count", "popularity", "poster_path", "backdrop_path"]  # ✅ 원하는 key 목록
              if key in movie_data["meta_data"]  # ✅ key가 존재할 경우만 추가
          }
      }
      for index, (_, movie_data) in enumerate(raw_results["movie_details"].items())
  }
  return results
