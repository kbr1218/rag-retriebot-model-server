# fetch_movie_details.py
from fastapi import HTTPException
from setup import movies_vectorstore

def fetch_movie_details(asset_ids: list):
  if movies_vectorstore is None:
    raise HTTPException(status_code=500, detail="movies vectorstore 로드 실패")
  
  # 영화 상세 정보를 담을 변수 선언
  movie_details = {}

  for asset_id in asset_ids:
    # asset_id와 일치하는 영화 정보 찾아서 results에 저장
    results = movies_vectorstore.similarity_search(query="",
                                                   k=1,
                                                   filter={"asset_id": asset_id})
    if results:
      doc = results[0]
      movie_details[asset_id] = {
        "page_content": doc.page_content,
        "metadata" : doc.metadata
      }
    else:
      movie_details[asset_id] = {"error": "영화 데이터를 찾을 수 없음"}

  return {"movie_details": movie_details}