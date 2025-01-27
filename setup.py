# setup.py
from langchain_teddynote import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import VECTORSTORE_PATH_MOVIE, VECTORSTORE_PATH_VIEW_100, LOGGING_NAME

# langsmith 추적 설정
logging.langsmith(LOGGING_NAME)

# 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings(model_name='ibm-granite/granite-embedding-278m-multilingual')

# 벡터스토어 로드
try:
    movies_vectorstore = FAISS.load_local(VECTORSTORE_PATH_MOVIE, embeddings=embeddings, allow_dangerous_deserialization=True)
    print(">>>>>> VectorStore for movies Loaded Successfully!")

    views_vectorstore = FAISS.load_local(VECTORSTORE_PATH_VIEW_100, embeddings=embeddings, allow_dangerous_deserialization=True)
    print(">>>>>> VectorStore for views Loaded Successfully!")
except Exception as e:
    print(f"❌ Error Loading VectorStore: {e}")
    movies_vectorstore = None  # 벡터스토어 로딩 실패 시 예외 처리는 여기에
    views_vectorstore = None