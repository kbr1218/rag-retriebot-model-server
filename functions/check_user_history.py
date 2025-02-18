# check_user_history.py
from functions.user_utils import find_user_vectors
from fastapi import FastAPI, HTTPException

def check_user_history(userid: str):
  user_history_data = {}
  try:
    # 벡터스토어에서 user_id 검색
    user_vectors = find_user_vectors(userid)
    print(user_vectors)
    if user_vectors:
      # 사용자의 데이터를 전역 변수에 저장
      user_history_data[userid] = user_vectors
      return user_history_data        # 200
    else:
      raise HTTPException(status_code=404, detail="user not found")                     # 404
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error checking user ID: {str(e)}")  # 500