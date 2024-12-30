# llm_modeltest1.py

### 0. 기본 설정 ###
import matplotlib.pyplot as plt

# 경고 메시지 출력 X
import warnings
warnings.filterwarnings("ignore")

# 한글 font 설정
import platform

if platform.system() == 'Darwin': # Mac 환경 폰트 설정
    plt.rc('font', family='AppleGothic')
elif platform.system() == 'Windows': # Windows 환경 폰트 설정
    plt.rc('font', family='Malgun Gothic')
    
plt.rcParams['axes.unicode_minus'] = False #한글 폰트 사용시 마이너스 폰트 깨짐 해결

# 글씨 선명하게 출력하는 설정

from IPython.display import set_matplotlib_formats
set_matplotlib_formats("retina")

# 랭체인 환경 설정
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate

from langchain_teddynote import logging

from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
import os


### 01. 환경변수 로드 ###
load_dotenv()
GEMINI_API_KEY = os.getenv('API_KEY_GEMINI')
LANGSMITH_API_KEY = os.getenv('LANGCHAIN_API_KEY')

# 랭스미스 추적 설정
logging.langsmith("lgdx_team2")


## 02. huggingface 임베딩 생성 및 벡터스토어 로드 ###
# HuggingFace 임베딩 생성
embeddings  = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")

# Chroma 벡터스토어 로드
vectorstore = Chroma(persist_directory="movie_4000_vectorstore", embedding_function=embeddings)


### 03. 랭체인 구성 ###
# 검색기 생성
retriever = vectorstore.as_retriever(
    search_type="mmr",   
    search_kwargs={"k": 20,              # 반환할 문서 수 (default: 4)
                   "fetch_k": 50,       # MMR 알고리즘에 전달할 문서 수
                   "lambda_mult": 0.5,    # 결과 다양성 조절 (default: 0.5),
                   }
)

# 프롬프트 템플릿 설정
template = """
You are a movie-recommendation chatbot.
You must only answer based on the given context.
Do not generate answers that are not directly supported by the context.

[Context]:
{retrieved_context}

[Question]:
{query}

[Answer]:
"""
prompt = ChatPromptTemplate.from_template(template)



# Google Gemini 모델 생성
def load_gemini(system_instruction):
    model = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0.3,
        max_tokens=5000,
        system_instruction=system_instruction,
        api_key=GEMINI_API_KEY
    )
    print(">>>>>>> model loaded...")
    return model


system_instruction = """you are a movie-recommendation chatbot. you must answer based on given data."""
llm = load_gemini(system_instruction)


# langchain 체인 구성
rag_chain = (
  {"query":RunnablePassthrough(),
    "retrieved_context": retriever,
  }
  # question(사용자의 질문) 기반으로 연관성이 높은 문서 retriever 수행 >> format_docs로 문서를 하나로 만듦
  | prompt               # 하나로 만든 문서를 prompt에 넘겨주고
  | llm                  # llm이 원하는 답변을 만듦
  | StrOutputParser()
)


### 04. 모델 테스트 ###
user_query='코미디 영화를 추천해줘'
response = rag_chain.invoke(user_query)
print(response)