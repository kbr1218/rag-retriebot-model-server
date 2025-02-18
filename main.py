# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chain.recommend import recommend_chain
from chain.post_recommend import post_recommend_chain
from chain.search import search_chain
from functions.add_views import add_view_to_vectorstore
from functions.fetch_movie_details import fetch_movie_details
from functions.filter_watched_content import filter_watched_contents
from functions.make_result import make_result
from functions.check_user_history import check_user_history
from functions.Light_FM import provide_score
import ast
import pickle
import lightfm as LightFM

app = FastAPI()

# 사용자 입력값 데이터 모델 정의
class UserInput(BaseModel):
  user_input: str

# 시청기록 저장용 데이터 모델 정의
class WatchInput(BaseModel):
  asset_id: str

user_history_data = {}
loaded_model = LightFM

@app.get('/')
def load_root():
  return {'hi': "model server is running(port: 8000)💭"}

@app.on_event("startup")
def startup_event():
  global loaded_model
  with open("./lightfm/adadelta_{'no_components'_ 25}.pkl", "rb") as f:
    loaded_model = pickle.load(f)
  print("저장된 모델을 성공적으로 불러왔습니다.")


# 사용자 ID 확인 및 시청기록 검색 API
@app.post('/{userid}/api/connect')
def check_user_id(userid: str):
  print("\n------------- CONNECT API 실행 -------------")
  global user_history_data

  try:
    # 벡터스토어에서 user_id 검색하여 최근 시청한 VOD를 최대 20개까지 가져옴
    user_history_data = check_user_history(userid)
    default_5_movies = provide_score(loaded_model, userid, user_history_data)

    if default_5_movies:
      return {"message": f"{userid}", 
              "movies": make_result(default_5_movies)} 
    else:
      raise HTTPException(status_code=404, detail="user not found")              # 404
    
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error checking user ID: {str(e)}")  # 500


# 추천요청 체인
@app.post('/{userid}/api/recommend')
def load_recommend(userid: str, user_input: UserInput):
  print("\n------------- RECOMMEND API 실행 -------------")

  # 1) 사용자 시청기록이 저장되어 있는지 먼저 확인
  if userid not in user_history_data:
    raise HTTPException(status_code=400, detail="사용자를 찾을 수 없음 (/api/connect 먼저 호출하쇼)")  # 400

  try:
    # 2) VOD 콘텐츠의 후보를 선정하는 체인 실행
    print(f">>>>>>>>> RECOMMEND CHAIN")
    response = recommend_chain.invoke(user_input.user_input)
    candidate_asset_ids = response.get("candidates", [])
    print(f">>>>>>>>> 후보로 선정된 콘텐츠 개수: {len(candidate_asset_ids)}")

    # 3) recommend chain에서 아무것도 가져오지 못한다면 최대 5번 실행
    for i in range(5):  
      if candidate_asset_ids:
        break
      print(f">>>>>>>>> RECOMMEND CHAIN ({i})")
      response = recommend_chain.invoke(user_input.user_input)
      candidate_asset_ids = response.get("candidates", [])
      print(f"\n>>>>>>>>> 후보로 선정된 콘텐츠의 asset IDs: \n{candidate_asset_ids}")

    if not candidate_asset_ids:
      raise HTTPException(status_code=500, detail="추천할 VOD 후보가 없습니다.")

    # 3) 후보 VOD 중 사용자가 시청한 콘텐츠를 제외하는 필터링 수행
    unwatched_candidates = filter_watched_contents(userid, candidate_asset_ids)
    print(f">>>>>>>>> 사용자가 시청한 콘텐츠를 제외한 콘텐츠 개수: {len(unwatched_candidates)}")


    # 4) post_recommend chain에 후보 콘텐츠 정보를 넣을 수 있도록 fetch_movie_details 함수 실행
    candidate_movies = fetch_movie_details(unwatched_candidates) if unwatched_candidates else []

    # 5) 사용자가 시청한 콘텐츠의 asset_id로 영화 정보를 가져오기
    watched_movies_asset_ids= [doc.metadata["asset_id"] for doc in user_history_data[userid]]
    watched_movies = fetch_movie_details(watched_movies_asset_ids)

    # 6) post_recommend chain의 prompt에 후보 콘텐츠 정보를 넣을 수 있도록 fetch_movie_details 함수 실행
    watched_movies_page_content = [doc.page_content for doc in user_history_data[userid]]
    user_preference = [
        f"asset_id: {movie_data['asset_id']}, use_tms/runtime: {movie_data['use_tms/runtime']}, datetime: {movie_data['datetime']}"
        for movie in watched_movies_page_content
        for movie_data in [ast.literal_eval(movie)]
    ]

    # 7) 사용자에게 추천할 콘텐츠 5개를 선별하는 체인 실행
    print(f"\n>>>>>>>>> POST RECOMMEND CHAIN")
    final_recommendation = post_recommend_chain.invoke(
      {"user_input": user_input.user_input,
       "candidate_movies": candidate_movies,
       "watched_movies": watched_movies,
       "user_preference": user_preference
      }
    )

    # 8) post_recommend_chain 실행 결괏값 asset_id로 추천 콘텐츠 상세정보 가져오기
    print(f">>>>>>>>> 최종 추천 VOD 개수: {len(final_recommendation['final_recommendations'])}")
    raw_results = fetch_movie_details(final_recommendation["final_recommendations"])

    return {
      "movies": make_result(raw_results),
      "answer": final_recommendation["response"]
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail = f"recommend API error: {str(e)}")  # 500

@app.post('/{userid}/api/search')
def load_search(userid: str, user_input: UserInput):
  print(f"\n------------- SEARCH API 실행 -------------")
  # 사용자 벡터 캐시 확인
  if userid not in user_history_data:
    raise HTTPException(status_code=400, detail="사용자를 찾을 수 없음 (/api/connect 먼저 호출하쇼)")
  try:
    response = search_chain.invoke(user_input.user_input)
    raw_results = fetch_movie_details(response["asset_id"])

    return {
      "movies": make_result(raw_results),
      "answer": response["answer"]
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail = f"search API error: {str(e)}")  # 500


# 시청기록 추가
@app.post('/{user_id}/api/watch')
def add_watch_record(user_id: str, watch_input: WatchInput):
  print(f"\n------------- WATCH API 실행 -------------")
  asset_id = watch_input.asset_id

  try:
    # 새로운 시청기록 추가
    return add_view_to_vectorstore(user_id, asset_id)
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"시청기록 추가 실패: {str(e)}")
