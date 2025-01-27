# add_views.py
from fastapi import HTTPException
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from datetime import datetime

def add_view_vectors(user_id: str, asset_id: str, views_vectorstore: FAISS, embeddings: Embeddings) -> None:
    """
    사용자 시청기록 벡터스토어에 새로운 값을 추가하는 함수

    Args:
        user_id (str): 시청한 사용자 ID
        asset_id (str): VOD ID
        views_vectorstore (FAISS): FAISS 벡터스토어 객체
        embeddings (Embeddings): 임베딩 함수
    """
    if views_vectorstore is None:
        raise HTTPException(status_code=500, detail="시청기록 벡터스토어 로드 실패")

    try:
        # metadata = {
        #     "user_id": user_id,
        #     "asset_id": asset_id,
        #     "use_tms/runtime": 1.0,  # 항상 1로 세팅
        #     "runtime": 
        #     "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # }
        # embedding = embeddings.embed_query(f"{user_id}_{asset_id}")

        # # Create a document and add it to the vectorstore
        # document = Document(page_content=f"View record for user {user_id} and asset {asset_id}", metadata=metadata)
        # views_vectorstore.add_documents([document], [embedding])

        return {"message": "연결테스트 성공"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding view record: {str(e)}")