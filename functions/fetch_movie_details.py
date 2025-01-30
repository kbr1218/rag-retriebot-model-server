# fetch_movie_details.py
from fastapi import HTTPException
from setup import movies_vectorstore

def fetch_movie_details(asset_ids: list):
  if movies_vectorstore is None:
    raise HTTPException(status_code=500, detail="movies vectorstore 로드 실패")
  
  # 영화 정보를 담을 변수 선언
  movie_details = {}
  for asset_id in asset_ids:
    # asset_id와 일치하는 영화 정보 찾아서 result에 저장
    results = movies_vectorstore.similarity_search_with_score(f"asset_id: {asset_id}", k=1)
    if results:
      movie_details[asset_id] = results[0]
    else:
      movie_details[asset_id] = None
  return movie_details