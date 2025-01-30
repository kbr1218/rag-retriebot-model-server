# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.recommend import recommend_chain
from api.post_recommend import post_recommend_chain
from setup import movies_vectorstore, views_vectorstore
from functions.user_utils import find_user_vectors
from functions.add_views import add_view_to_vectorstore
from functions.fetch_movie_details import fetch_movie_details

app = FastAPI()

# 사용자 입력값 데이터 모델 정의
class UserInput(BaseModel):
  user_input: str

# 시청기록 저장용 데이터 모델 정의
class WatchInput(BaseModel):
  asset_id: str
  runtime: float

# 사용자 시청기록 데이터 변수
user_data_cache = {}

@app.get('/')
def load_root():
  return {'hi': "model server is running(port: 8000)💭"}


# 사용자 ID 확인 및 시청기록 검색
@app.post('/{userid}/api/connect')
def check_user_id(userid: str):
  try:
    # 벡터스토어에서 user_id 검색
    user_vectors = find_user_vectors(userid)
    if user_vectors:
      # 사용자의 데이터를 전역 변수에 저장
      user_data_cache[userid] = user_vectors
      return {"message": f"{userid}", "records_found": len(user_vectors)}        # 200
    else:
      raise HTTPException(status_code=404, detail="user not found")              # 404
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error checking user ID: {str(e)}")  # 500

# 추천요청 체인
@app.post('/{userid}/api/recommend')
def load_recommend(userid: str, user_input: UserInput):
  print("recommend API 실행 시작 여기부터")
  # 영화 벡터스토어가 없는 경우
  if movies_vectorstore is None:
    raise HTTPException(status_code=500, detail="Vectorstore for movies not loaded.")  # 500

  # 사용자 벡터 캐시 확인
  if userid not in user_data_cache:
    raise HTTPException(status_code=400, detail="사용자를 찾을 수 없음 (/api/connect 먼저 호출하쇼)")

  try:
    # VOD 콘텐츠의 후보를 선정하는 체인 실행
    response = recommend_chain.invoke(user_input.user_input)
    candidate_asset_ids = response.get("candidates", [])

    if not candidate_asset_ids:
      raise HTTPException(status_code=500, detail="추천할 VOD 후보가 없습니다.")

    candidate_movies = fetch_movie_details(candidate_asset_ids)
    print(f">>>>>>>>> {candidate_asset_ids}")

    # 사용자가 시청한 VOD의 asset_id를 변수에 저장
    watched_movies_asset_ids = [doc.metadata["asset_id"] for doc, _ in user_data_cache[userid]]
    watched_movies = fetch_movie_details(watched_movies_asset_ids)
    print(f">>>>>>>>> {watched_movies_asset_ids}")

    if not candidate_movies:
      raise HTTPException(status_code=500, detail="추천 VOD 정보가 존재하지 않습니다.")
    if not watched_movies:
      raise HTTPException(status_code=500, detail="시청한 VOD 정보가 존재하지 않습니다.")

    # 사용자 시청기록을 사용하여 후보 VOD 중 5개 선정
    final_recommendation = post_recommend_chain.invoke(
      {"user_input": user_input.user_input,
       "candidate_movies": candidate_movies,
       "watched_movies": watched_movies
      }
    )

    return final_recommendation
  except Exception as e:
    raise HTTPException(status_code=500, detail = f"recommend API error: {str(e)}")  # 500
  

# 시청기록 추가
@app.post('/{user_id}/api/watch')
def add_watch_record(user_id: str, watch_input: WatchInput):
  asset_id = watch_input.asset_id
  runtime = watch_input.runtime

  if views_vectorstore is None:
      raise HTTPException(status_code=500, detail="Vectorstore not loaded.")

  try:
    # 새로운 시청기록 추가
    add_view_to_vectorstore(user_id, asset_id, runtime)
    return {"message": f"시청기록 추가 완료 >> {user_id} - {asset_id}"}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"시청기록 추가 실패: {str(e)}")
