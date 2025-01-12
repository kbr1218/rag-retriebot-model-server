# recommend.py
from dotenv import load_dotenv
import os

from langchain_teddynote import logging
from operator import itemgetter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS


# API KEY 정보 로드
load_dotenv()
GEMINI_API_KEY = os.getenv('API_KEY_GEMINI')
OPENAI_API_KEY = os.getenv('API_KEY_OPENAI')

# LangSmith 추적 설정
logging.langsmith("lgdx_team2_routerchain")

# 임베딩 모델 생성
embeddings = HuggingFaceEmbeddings(model_name='ibm-granite/granite-embedding-278m-multilingual')

# 벡터스토어 로드
new_vector_store = FAISS.load_local("db\movies_vectorstore_faiss_1500",
                                    embeddings=embeddings,
                                    allow_dangerous_deserialization=True)

# StructuredOutputParser 사용
recommend_response_schemas = [
  ResponseSchema(name="candidates",
                 description="사용자의 입력에 맞게 추천할 VOD 콘텐츠의 인덱스 리스트. 예: [1, 10, 31, 89, 135, 180]")
]
output_parser = StructuredOutputParser.from_response_schemas(recommend_response_schemas)

# 출력 지시사항 파싱
recommend_chain_format_instructions = output_parser.get_format_instructions()

# 검색기 생성
recommend_chain_retriever = new_vector_store.as_retriever(
    search_type="mmr",   
    search_kwargs={"k": 20,              # 반환할 문서 수 (default: 4)
                   "fetch_k": 50,       # MMR 알고리즘에 전달할 문서 수
                   "lambda_mult": 0.8,  # 결과 다양성 조절 (default: 0.5),
                   }
)


# 프롬프트 템플릿 설정
recommend_chain_template = """
You are a movie-recommendation chatbot.
You must only answer based on the given context.
Do not generate answers that are not directly supported by the context.
사용자의 요청에 따라 추천할 VOD 콘텐츠의 **인덱스 리스트**를 반환하세요.

**중요**:
- 추천 리스트에는 반드시 **[Context]**에서 제공된 문서만 포함해야 합니다.
- **[Context]**에 없는 문서를 절대 생성하거나 포함하지 마세요.
- **[Context]**에 적절한 추천이 없을 경우, 빈 리스트를 반환하세요.

응답은 JSON 형식으로 **오직 추천된 콘텐츠의 인덱스 리스트**만 포함해야 합니다.
{recommend_chain_format_instructions}
---
예제 출력 형식:
```json
{{"candidates": [1, 10, 31, 89, 135, 180]}}```
(만약 적절한 추천이 없을 경우)
```json
{{"candidates": []}}```

[사용자 입력과 사용자 입력값의 유형]:
{formatted_string}

[Context]:
{recommend_chain_retriever}

[Answer]:
"""
recommend_chain_prompt = ChatPromptTemplate.from_template(recommend_chain_template,
                                                          partial_variables={'recommend_chain_format_instructions': recommend_chain_format_instructions})
# LLM 모델 생성 (1. GEMINI 2. OpenAI)
def load_gemini(system_instruction):
    model = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0.3,
        max_tokens=5000,
        system_instruction=system_instruction,
        api_key=GEMINI_API_KEY
    )
    print(">>>>>>> Gemini loaded from recommend chain...")
    return model

def load_gpt(system_instruction):
    model = ChatOpenAI(
        model_name='gpt-4o-mini-2024-07-18',
        temperature=0,
        max_tokens=3000,
        api_key=OPENAI_API_KEY
    )
    print(">>>>>>> GPT loaded from recommend chain...")
    return model

system_instruction = """you are a movie-recommendation chatbot. you must answer based on given data."""
recommend_chain_llm = load_gemini(system_instruction)

# 딕셔너리 자료형을 string으로 변환하는 함수
def format_change(classification_result: dict, user_input: str) -> str:
    type_value = classification_result.get("classification_result", {}).get("type", "일반대화")

    # string 자료형으로 변경
    formatted_str = f"type: '{type_value}', user_input: '{user_input}'"
    return formatted_str

# langchain 체인 구성
recommend_chain = (
  {"formatted_string":RunnablePassthrough(),
    "recommend_chain_retriever": recommend_chain_retriever,
  }
  | recommend_chain_prompt               # 하나로 만든 문서를 prompt에 넘겨주고
  | recommend_chain_llm                  # llm이 원하는 답변을 만듦
  | output_parser
)