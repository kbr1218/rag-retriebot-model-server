# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chain.recommend import recommend_chain
from chain.post_recommend import post_recommend_chain
from functions.user_utils import find_user_vectors
from functions.add_views import add_view_to_vectorstore
from functions.fetch_movie_details import fetch_movie_details
from functions.convert_to_json import convert_to_json
import json
from db import redis_helper
import pickle
import lightfm as LightFM
import pandas as pd 
import numpy as np
import heapq

app = FastAPI()

# 사용자 입력값 데이터 모델 정의
class UserInput(BaseModel):
  user_input: str

# 시청기록 저장용 데이터 모델 정의
class WatchInput(BaseModel):
  asset_id: str
  runtime: float

# 사용자 추천 algorithm score
user_data_score_cache = {}
loaded_model = LightFM

@app.get('/')
def load_root():
  return {'hi': "model server is running(port: 8000)💭"}

# Redis 서버 실행
# @app.on_event("startup")
# def startup_event():
#     global user_data_score_cache
#     """
#     FastAPI 서버가 시작될 때 CSV 데이터를 Redis에 저장(없으면 로드)한 후,
#     Redis에서 데이터를 읽어 전역 캐시(user_data_score_cache)에 저장합니다.
#     """
#     redis_helper.load_csv_to_redis()
#     user_data_score_cache = redis_helper.get_csv()
#     print(user_data_score_cache)
#     print(f"캐시에 로드된 데이터 개수: {len(user_data_score_cache)}")
    
@app.on_event("startup")
def startup_event():
  global loaded_model
  with open("lightfm_model.pkl", "rb") as f:
    loaded_model = pickle.load(f)
  print("저장된 모델을 성공적으로 불러왔습니다.")

# @app.get("/get_csv")
# def endpoint_get_csv():
#     """Redis에서 CSV 데이터를 가져오는 엔드포인트"""
#     return redis_helper.get_csv()


@app.get("/cache")
def show_cache():
    """전역 캐시된 데이터를 확인할 수 있는 엔드포인트"""
    return {"cached_data": user_data_score_cache}
    # user:101 → ['{"asset_id": "A", "asset_score": 0.9}', '{"asset_id": "B", "asset_score": 0.8}']

# 사용자 ID 확인 및 시청기록 검색 API
@app.post('/{userid}/api/connect')
def check_user_id(userid: str):
  print("\n------------- CONNECT API 실행 -------------")
  # 사용자 영화 Score을 전역 변수 user_data_socre_cache에 저장
  global user_data_score_cache
  try:
    
    # LightFM 사용할 컬럼 user_ids, asset_ids 로드
    user_ids = pd.read_csv("db/user_mapping.csv")
    asset_ids = pd.read_csv("db/asset_mapping.csv")
    print("csv load 성공!")
    
    # post로 받은 userid를 쿼리하기 위해 DataFrame으로 변환
    user_df = pd.DataFrame(user_ids)
    user_index = user_df.query("user_id == @userid")["user_index"].values[0]
    print(user_index)

    # 모든 아이템에 대한 예측 점수 계산
    scores = loaded_model.predict(int(user_index), np.array(asset_ids["asset_index"]))

    # 추천 아이템
    print(f"{scores} LightFM 추천 완료!")

    # ✅ 결과를 DataFrame으로 정리
    df_recommendations = pd.DataFrame({
      "asset_id": asset_ids["asset_id"],
      "asset_index": asset_ids["asset_index"],
      "score": scores
      }).sort_values(by="score", ascending=False)
    
    user_data_score_cache = df_recommendations.set_index("asset_id")["score"].to_dict()
    print(f">>>> check here: {user_data_score_cache}")


    if user_data_score_cache:
      return {"message": f"{userid}", "records_found": len(user_data_score_cache)}        # 200
    else:
      raise HTTPException(status_code=404, detail="user not found")              # 404
    
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error checking user ID: {str(e)}")  # 500


# 추천요청 체인
@app.post('/{userid}/api/recommend')
def load_recommend(userid: str, user_input: UserInput):
  print("\n------------- RECOMMEND API 실행 -------------")
  global user_data_score_cache

  try:
    # 2) VOD 콘텐츠의 후보를 선정하는 체인 실행
    print(f">>>>>>>>> RECOMMEND CHAIN")
    response = recommend_chain.invoke(user_input.user_input)
    candidate_asset_ids = response.get("candidates", [])
    print(f"\n>>>>>>>>> 후보로 선정된 콘텐츠의 asset IDs: \n{candidate_asset_ids}")

    if not candidate_asset_ids:
      raise HTTPException(status_code=500, detail="추천할 VOD 후보가 없습니다.")

  
    # 3) 사용자가 시청한 콘텐츠의 asset_id를 user_data_score_cache에서 가져와 변수에 저장
    watched_movies_asset_ids = user_data_score_cache.keys()
    # print(f"\n>>>>>>>>> 사용자가 시청한 콘텐츠의 asset IDs: \n{watched_movies_asset_ids}")

    # ✅ LLM 리스트에서 존재하는 영화만 필터링 후, heap을 사용하여 5개만 유지
    top_5_movies = heapq.nlargest(
        5,  # 5개 선택
        [(movie, user_data_score_cache[movie]) for movie in candidate_asset_ids if movie in user_data_score_cache],  # 필터링된 영화 리스트
        key=lambda x: x[1]  # 점수 기준 정렬
    )

    top_5_movies = ([tup[0] for tup in top_5_movies])
    # ✅ 결과 출력
    print(top_5_movies)


    # 4) VOD 콘텐츠 후보 중에서 사용자가 시청한 콘텐츠가 있다면 제외
    watched_set = set(watched_movies_asset_ids)
    candidate_asset_ids = [asset_id for asset_id in candidate_asset_ids if asset_id not in watched_set]
    print("콘텐츠 제외 완료")
    # 5) post_recommend chain의 prompt에 후보 콘텐츠 정보를 넣을 수 있도록 fetch_movie_details 함수 실행
    candidate_movies = fetch_movie_details([tup[0] for tup in top_5_movies])
    print("candidate 완료")
    # 6) post_recommend chain의 prompt에 사용자가 시청한 콘텐츠 정보를 넣을 수 있도록 fetch_movie_details 함수 실행
    watched_movies = fetch_movie_details(top_5_movies)
    print("fetch 완료")

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
      str(index + 1): convert_to_json(json.loads(movie_data["page_content"]))
      for index, (_, movie_data) in enumerate(raw_results["movie_details"].items())
    }

    return {
      "movies": results,
      "answer": final_recommendation["response"]
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail = f"recommend API error: {str(e)}")  # 500
    print("h")
  

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
