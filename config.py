# config.py
from dotenv import load_dotenv
import os

# API KEY 정보 로드
load_dotenv()
GEMINI_API_KEY = os.getenv('API_KEY_GEMINI')
OPENAI_API_KEY = os.getenv('API_KEY_OPENAI')

# FAISS 벡터스토어 path
VECTORSTORE_PATH = "db\movies_vectorstore_faiss_1500"

# LangSmith logging proj. name
LOGGING_NAME = "lgdx_team2_routerchain"
