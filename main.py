# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chain.recommend import recommend_chain
from chain.post_recommend import post_recommend_chain
from functions.user_utils import find_user_vectors
from functions.add_views import add_view_to_vectorstore
from functions.fetch_movie_details import fetch_movie_details
# from functions.string_to_json import convert_string_to_json
import json

app = FastAPI()

# 사용자 입력값 데이터 모델 정의
class UserInput(BaseModel):
  user_input: str

# 시청기록 저장용 데이터 모델 정의
class WatchInput(BaseModel):
  asset_id: str
  runtime: float

# 사용자 시청기록 저장을 위한 변수
user_data_cache = {}

@app.get('/')
def load_root():
  return {'hi': "model server is running(port: 8000)💭"}


# 사용자 ID 확인 및 시청기록 검색 API
@app.post('/{userid}/api/connect')
def check_user_id(userid: str):
  print("\n------------- CONNECT API 실행 -------------")
  try:
    # 벡터스토어에서 user_id 검색
    user_vectors = find_user_vectors(userid)

    if user_vectors:
      # 사용자 시청기록을 전역 변수(user_data_cache)에 저장
      user_data_cache[userid] = user_vectors
      return {"message": f"{userid}", "records_found": len(user_vectors)}        # 200
    else:
      raise HTTPException(status_code=404, detail="user not found")              # 404
    
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error checking user ID: {str(e)}")  # 500


# 추천요청 체인
@app.post('/{userid}/api/recommend')
def load_recommend(userid: str, user_input: UserInput):
  print("\n------------- RECOMMEND API 실행 -------------")

  # 1) 사용자 시청기록이 저장되어 있는지 먼저 확인
  if userid not in user_data_cache:
    raise HTTPException(status_code=400, detail="사용자를 찾을 수 없음 (/api/connect 먼저 호출하쇼)")  # 400

  try:
    # 2) VOD 콘텐츠의 후보를 선정하는 체인 실행
    print(f">>>>>>>>> RECOMMEND CHAIN")
    response = recommend_chain.invoke(user_input.user_input)
    candidate_asset_ids = response.get("candidates", [])
    print(f"\n>>>>>>>>> 후보로 선정된 콘텐츠의 asset IDs: \n{candidate_asset_ids}")

    if not candidate_asset_ids:
      raise HTTPException(status_code=500, detail="추천할 VOD 후보가 없습니다.")

    # 3) 사용자가 시청한 콘텐츠의 asset_id를 user_data_cache에서 가져와 변수에 저장
    watched_movies_asset_ids = [doc.metadata["asset_id"] for doc in user_data_cache[userid]]
    print(f"\n>>>>>>>>> 사용자가 시청한 콘텐츠의 asset IDs: \n{watched_movies_asset_ids}")

    # 4) VOD 콘텐츠 후보 중에서 사용자가 시청한 콘텐츠가 있다면 제외
    watched_set = set(watched_movies_asset_ids)
    candidate_asset_ids = [asset_id for asset_id in candidate_asset_ids if asset_id not in watched_set]

    # 5) post_recommend chain의 prompt에 후보 콘텐츠 정보를 넣을 수 있도록 fetch_movie_details 함수 실행
    candidate_movies = fetch_movie_details(candidate_asset_ids)

    # 6) post_recommend chain의 prompt에 사용자가 시청한 콘텐츠 정보를 넣을 수 있도록 fetch_movie_details 함수 실행
    watched_movies = fetch_movie_details(watched_movies_asset_ids)

    # 7) 사용자에게 추천할 콘텐츠 5개를 선별하는 체인 실행
    print(f"\n>>>>>>>>> POST RECOMMEND CHAIN")
    final_recommendation = post_recommend_chain.invoke(
      {"user_input": user_input.user_input,
       "candidate_movies": candidate_movies,
       "watched_movies": watched_movies
      }
    )

    # 7) post_recommend_chain 실행 결괏값 asset_id로 추천 콘텐츠 상세정보 가져오기
    raw_results = fetch_movie_details(final_recommendation["final_recommendations"])
    print(f"\n>>>>>>>>> raw_results HERE: \n{raw_results}")

    # 8) 클라이언트에게 전송할 수 있도록 JSON 형식으로 변환
    results = {
      str(index + 1): json.loads(movie_data["page_content"])
      for index, (_, movie_data) in enumerate(raw_results["movie_details"].items())
    }

    return {
      "movies": results,
      "response": final_recommendation["response"]
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail = f"recommend API error: {str(e)}")  # 500
  

# 시청기록 추가
@app.post('/{user_id}/api/watch')
def add_watch_record(user_id: str, watch_input: WatchInput):
  print(f"\n------------- WATCH API 실행 -------------")
  asset_id = watch_input.asset_id
  runtime = watch_input.runtime

  try:
    # 새로운 시청기록 추가
    add_view_to_vectorstore(user_id, asset_id, runtime)
    return {"message": f"시청기록 추가 완료 >> {user_id} - {asset_id}"}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"시청기록 추가 실패: {str(e)}")
