# setup.py
from langchain_teddynote import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config import LOGGING_NAME, VECTORSTORE_PATH_MOVIE
import yaml

# langsmith 추적 설정
logging.langsmith(LOGGING_NAME)

# 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings(model_name='ibm-granite/granite-embedding-278m-multilingual')

# 벡터스토어 로드
try:
    movies_vectorstore = Chroma(persist_directory=VECTORSTORE_PATH_MOVIE,
                                embedding_function=embeddings)
    print(">>>>>> VectorStore for movies Loaded Successfully!")

except Exception as e:
    print(f"❌ Error Loading VectorStore: {e}")
    movies_vectorstore = None  # 벡터스토어 로딩 실패 시 예외 처리는 여기에
    views_vectorstore = None

# yaml에서 template 불러오는 함수
def load_template_from_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data['template']