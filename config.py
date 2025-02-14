# config.py
from dotenv import load_dotenv
import os

# API KEY 정보 로드
load_dotenv()
GEMINI_API_KEY = os.getenv('API_KEY_GEMINI')
OPENAI_API_KEY = os.getenv('API_KEY_OPENAI')

# FAISS 벡터스토어 path
VECTORSTORE_PATH_MOVIE = "db/movies_vectorstore_chroma_1630_json"
VECTORSTORE_PATH_VIEW_1000 = "db/views_vectorstore_chroma_valid_1000"
VECTORSTORE_PATH_VIEW_1 = "db/views_vectorstore_chroma_first"   # user000001 ~ user017438
VECTORSTORE_PATH_VIEW_2 = "db/views_vectorstore_chroma_second"  # user017439 ~ user041480

# LangSmith logging proj. name
LOGGING_NAME = "lgdx_team2_routerchain"
