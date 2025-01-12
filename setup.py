# setup.py
from langchain_teddynote import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import VECTORSTORE_PATH

# langsmith 추적 설정
logging.langsmith("lgdx_team2_routerchain")

# 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings(model_name='ibm-granite/granite-embedding-278m-multilingual')

# 벡터스토어 로드
try:
    FAISS_vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings=embeddings, allow_dangerous_deserialization=True)
    print(">>>>>> FAISS VectorStore Loaded Successfully!")
except Exception as e:
    print(f"❌ Error Loading FAISS VectorStore: {e}")
    FAISS_vectorstore = None  # 벡터스토어 로딩 실패 시 예외 처리는 여기에