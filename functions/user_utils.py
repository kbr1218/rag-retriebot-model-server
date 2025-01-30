# user_utils.py
from typing import List, Tuple
from fastapi import HTTPException
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from setup import embeddings, views_vectorstore

def find_user_vectors(user_id: str) -> List[Tuple[Document, float]]:
  """
  user_id에 해당하는 벡터들을 벡터스토어에서 검색하는 함수

  Args:
      user_id (str): 검색할 사용자 ID.
      
  Returns:
      List[Tuple[Document, float]]: 주어진 user_id에 해당하는 Document와 유사도 점수의 리스트
  """
  if views_vectorstore is None:
    raise HTTPException(status_code=500, detail="Vectorstore not loaded.")
  
  try:
    # user_id에 해당하는 벡터 검색
    query_embedding = embeddings.embed_query(user_id)
    search_results = views_vectorstore.similarity_search_with_score_by_vector(query_embedding, k=views_vectorstore.index.ntotal)

    # user_id와 일치하는 메타데이터를 가진 결과 필터링
    user_vectors = [(doc, score) for doc, score in search_results if doc.metadata.get("user_id") == user_id]
    print(user_vectors)
    return user_vectors
  
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"벡터스토어에서 사용자 벡터를 검색하는 중 오류 발생: {str(e)}")