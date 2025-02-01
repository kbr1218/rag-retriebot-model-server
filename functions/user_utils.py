# user_utils.py
from typing import List, Tuple
from fastapi import HTTPException
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from setup import embeddings
from config import VECTORSTORE_PATH_VIEW_1, VECTORSTORE_PATH_VIEW_2


def find_user_vectors(user_id: str) -> List[Tuple[Document, float]]:
  """
  user_id에 해당하는 벡터들을 벡터스토어에서 검색하는 함수

  Args:
      user_id (str): 검색할 사용자 ID.
  """
  # 시청기록 벡터스토어 먼저 불러오기
  user_number = int(user_id.replace("user", ""))
  print(f">>>>>> user_number: {user_number}")

  # 범위에 따라 벡터스토어 로드
  if 1 <= user_number <= 17438:
    views_vectorstore = Chroma(persist_directory=VECTORSTORE_PATH_VIEW_1,
                               embedding_function=embeddings)
    print(">>>>>> VectorStore for view #1 Loaded Successfully!")
  elif 17439 <= user_number <= 41480:
    views_vectorstore = Chroma(persist_directory=VECTORSTORE_PATH_VIEW_2,
                               embedding_function=embeddings)
    print(">>>>>> VectorStore for view #2 Loaded Successfully!")
  else:
    raise HTTPException(status_code=500, detail="vectorstore not loaded ({user_id}: 범위를 벗어난 userID)")
  
  try:
    total_docs = views_vectorstore._collection.count()
    # user_id에 해당하는 벡터 검색
    user_vectors = views_vectorstore.similarity_search(query="",
                                                       k=total_docs,
                                                       filter={"user_id": user_id})
    print(user_vectors)
    return user_vectors
  
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"벡터스토어에서 사용자 벡터를 검색하는 중 오류 발생: {str(e)}")