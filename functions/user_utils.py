# user_utils.py
from typing import List, Tuple
from fastapi import HTTPException
from langchain_core.documents import Document
import setup

def find_user_vectors(user_id: str) -> List[Tuple[Document, float]]:
  """
  user_id에 해당하는 벡터들을 벡터스토어에서 검색하는 함수

  Args:
      user_id (str): 검색할 사용자 ID.

  Returns:
      List[Tuple[Document, float]]: 최근 10개의 시청 기록 벡터.
  """
  # 시청기록 벡터스토어 먼저 불러오기

  if setup.views_vectorstore is None:
    setup.views_vectorstore = setup.load_views_vectorstore(user_id)
  
  try:
    # user_id에 해당하는 벡터 검색
    user_vectors = setup.views_vectorstore.similarity_search(query="",  # 또는  max_marginal_relevance_search
                                                        k=10,
                                                        filter={"user_id": user_id})
    print(f"\n>>>>>>>>> 사용자의 시청기록: {user_vectors}")
    return user_vectors
  
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"벡터스토어에서 사용자 벡터를 검색하는 중 오류 발생: {str(e)}")