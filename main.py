# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from api.recommend import recommend_chain
from setup import movies_vectorstore, views_vectorstore, embeddings
from functions.user_utils import find_user_vectors

app = FastAPI()

# 사용자 입력값 데이터 모델 정의
class UserInput(BaseModel):
  user_input: str

# 사용자 데이터를 저장할 변수 (시청기록)
user_data_cache = {}

@app.get('/')
def load_root():
  return {'hi': "model server is running(port: 8000)💭"}


# 사용자 ID 확인 및 시청기록 저장
@app.post('/{userid}/api/connect')
def check_user_id(userid: str):
  try:
    # 벡터스토어에서 user_id 검색
    user_vectors = find_user_vectors(userid, views_vectorstore, embeddings)
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
  # 영화 벡터스토어가 없는 경우
  if movies_vectorstore is None:
    raise HTTPException(status_code=500, detail="Vectorstore for movies not loaded.")  # 500

  # 사용자 벡터 캐시 확인
  if userid not in user_data_cache:
    raise HTTPException(status_code=400, detail="사용자를 찾을 수 없음 (/api/connect 먼저 호출하쇼)")

  # 추천 체인
  try:
    user_vectors = user_data_cache[userid] 
    response = recommend_chain.invoke(user_input.user_input)
    return response
  except Exception as e:
    raise HTTPException(status_code=500, detail = f"recommend chain error: {str(e)}")  # 500