# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from api.recommend import recommend_chain
from setup import FAISS_vectorstore

app = FastAPI()

# 사용자 입력값(데이터 모델) 정의
class UserInput(BaseModel):
  user_input: str

@app.get('/')
def load_root():
  return {'hi': "model server is running(port: 8000)💭"}

# 추천요청 체인
@app.post('/api/{userid}/recommend')
def load_recommend(user_input: UserInput):
  if FAISS_vectorstore is None:
      return {'error': "Vector store not loaded."}
  
  response = recommend_chain.invoke(user_input.user_input)
  return response