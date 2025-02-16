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
import pickle
import lightfm as LightFM
import pandas as pd 
import numpy as np
from chain.search import search_chain
from collections import Counter
from functions.check_user_history import check_user_history
from functions.page_content_parser import parse_page_content
from functions.make_result import make_result_for_db1, make_result_for_db2
from functions.Light_FM import provide_score

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
user_history_data = {}
loaded_model = LightFM

@app.get('/')
def load_root():
  return {'hi': "model server is running(port: 8000)💭"}
    
@app.on_event("startup")
def startup_event():
  global loaded_model
  with open("lightfm_20_0.02865.pkl", "rb") as f:
    loaded_model = pickle.load(f)
  print("저장된 모델을 성공적으로 불러왔습니다.")


@app.get("/cache")
def show_cache():
    """전역 캐시된 데이터를 확인할 수 있는 엔드포인트"""
    return {"cached_data": user_data_score_cache}
    # user:101 → ['{"asset_id": "A", "asset_score": 0.9}', '{"asset_id": "B", "asset_score": 0.8}']


# 사용자 ID 확인 및 시청기록 검색 API
@app.post('/{userid}/api/connect')
def check_user_score(userid: str):
  print("\n------------- CONNECT API 실행 -------------")
  # 사용자 영화 Score을 전역 변수 user_data_socre_cache에 저장
  global user_history_data
  try:
    # user 시청기록 가져와서 전역변수에 할당
    user_history_data = check_user_history(userid)

    # ✅ 결과 출력
    default_5_movies = provide_score(loaded_model, userid, user_history_data)

    if default_5_movies:
      return {"message": f"{userid}", 
              "movies": make_result_for_db2(default_5_movies)
             }        # 200
    else:
      raise HTTPException(status_code=404, detail="user not found")              # 404
    
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error checking user ID: {str(e)}")  # 500

  

# 추천요청 체인
@app.post('/{userid}/api/recommend')
def load_recommend(userid: str, user_input: UserInput):
  print("\n------------- RECOMMEND API 실행 -------------")
  
  global user_history_data
  print(f"--------------------user_history_data{user_history_data}")
  try:
    # VOD 콘텐츠의 후보를 선정하는 체인 실행
    print(f">>>>>>>>> RECOMMEND CHAIN")
    response = recommend_chain.invoke(user_input.user_input)
    print(response)

    candidate_asset_ids = response.get("candidates", [])
    print(f"\n>>>>>>>>> 후보로 선정된 콘텐츠의 asset IDs: \n{candidate_asset_ids}")

    for _ in range(5):  
      if candidate_asset_ids:
        break
      print(f">>>>>>>>> RECOMMEND CHAIN")
      response = recommend_chain.invoke(user_input.user_input)
      candidate_asset_ids = response.get("candidates", [])
      print(f"\n>>>>>>>>> 후보로 선정된 콘텐츠의 asset IDs: \n{candidate_asset_ids}")

    if not candidate_asset_ids:
      print("채팅을 다시 입력해줘 멍멍")
      raise HTTPException(status_code=500, detail="추천할 VOD 후보가 없습니다.")

    # 시청기록의 중복 asset_id를 지우고, asset_id의 list를 얻기
    watched_movies_asset_ids = set([doc.metadata["asset_id"] for doc in user_history_data[userid]])
    print(f"----------------여기 watched_movies_asset_ids: {watched_movies_asset_ids}")

    # post_recommend chain의 prompt에 사용자가 시청한 콘텐츠 정보를 넣을 수 있도록 fetch_movie_details 함수 실행
    watched_movies = fetch_movie_details(watched_movies_asset_ids)
    print(f"----------------여기 watched_movies: {watched_movies}")

    # 시청한 asset_id 제외
    candidate_asset_ids = [asset_id for asset_id in candidate_asset_ids if asset_id not in watched_movies_asset_ids]
    print("콘텐츠 제외 완료")  

    # post_recommend chain의 prompt에 최종 5개 콘텐츠 정보를 넣을 수 있도록 fetch_movie_details 함수 실행
    final_candidate_movies = fetch_movie_details(candidate_asset_ids)
    print(f"----------------여기 final_candidate_movies: {final_candidate_movies}")

    # 7) 사용자에게 추천할 콘텐츠 5개를 선별하는 체인 실행
    print(f"\n>>>>>>>>> POST RECOMMEND CHAIN")
    final_recommendation = post_recommend_chain.invoke(
      {"user_input": user_input.user_input,
       "final_candidate_movies": final_candidate_movies,
       "watched_movies": watched_movies
      }
    )
    
    # 7) post_recommend_chain 실행 결괏값 asset_id로 추천 콘텐츠 상세정보 가져오기 -> db1
    # raw_results = fetch_movie_details(final_recommendation["final_recommendations"])
    # print(f"\n>>>>>>>>> raw_results HERE: \n{raw_results}")

    # 7) post_recommend_chain 실행 결괏값 asset_id로 추천 콘텐츠 상세정보 가져오기 -> db2
    raw_results = fetch_movie_details(final_recommendation["final_recommendations"])
    print(f"\n>>>>>>>>> raw_results HERE: \n{raw_results}")

    return {
      "movies": make_result_for_db2(raw_results),
      "answer": final_recommendation["response"]
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail = f"recommend API error: {str(e)}")  # 500
  
  

@app.post('/{userid}/api/search')
def search_invoke(userid: str, user_input: UserInput):
  print("search API 실행 시작 여기부터")

  try:
    response = search_chain.invoke(user_input.user_input)
    raw_results = fetch_movie_details(response["asset_id"])

    print(f"\n>>>>>>>>> raw_results HERE: \n{raw_results}")
    # 8) 클라이언트에게 전송할 수 있도록 JSON 형식으로 변환- 보리코드----
    results = {
      str(index + 1): convert_to_json(json.loads(movie_data["page_content"]))
      for index, (_, movie_data) in enumerate(raw_results["movie_details"].items())
    }

    return {
      "movies": results,
      "answer": response["reason"]
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail = f"search API error: {str(e)}")  # 500
  

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