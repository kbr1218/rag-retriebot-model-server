# recommend.py
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from setup import FAISS_vectorstore
from config import GEMINI_API_KEY, OPENAI_API_KEY

# StructuredOutputParser 사용
recommend_response_schemas = [
  ResponseSchema(name="candidates",
                 description="사용자의 입력에 맞게 추천할 VOD 콘텐츠의 인덱스 리스트. 예: [1, 10, 31, 89, 135, 180]")
]
output_parser = StructuredOutputParser.from_response_schemas(recommend_response_schemas)

# 출력 지시사항 파싱
recommend_chain_format_instructions = output_parser.get_format_instructions()


# LLM 모델 생성 (1. GEMINI 2. OpenAI)
def load_gemini():
    model = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0.3,
        max_tokens=5000,
        api_key=GEMINI_API_KEY
    )
    print(">>>>>>> Gemini loaded from recommend chain...")
    return model

def load_gpt():
    model = ChatOpenAI(
        model_name='gpt-4o-mini-2024-07-18',
        temperature=0,
        max_tokens=3000,
        api_key=OPENAI_API_KEY
    )
    print(">>>>>>> GPT loaded from recommend chain...")
    return model
# system_instruction = """you are a movie-recommendation chatbot. you must answer based on given data."""

# 검색기 생성
multiquery_chain_retriever = MultiQueryRetriever.from_llm(
    retriever = FAISS_vectorstore.as_retriever(
        search_type="similarity",   
        search_kwargs={"k": 20,              # 반환할 문서 수 (default: 4)
                      #  "fetch_k": 50,        # MMR 알고리즘에 전달할 문서 수
                      #  "lambda_mult": 0.8,   # 결과 다양성 조절 (default: 0.5),
                       }
    ),
    llm = load_gemini()
)


# 프롬프트 템플릿 설정
recommend_chain_template = """
You are a movie-recommendation chatbot.
You must only answer based on the given context.
Do not generate answers that are not directly supported by the context.
사용자의 요청에 따라 추천할 VOD 콘텐츠 **asset_id의 리스트**를 반환하세요.

**중요**:
- 추천 리스트에는 반드시 **[Context]**에서 제공된 문서만 포함해야 합니다.
- **[Context]**에 없는 문서를 절대 생성하거나 포함하지 마세요.
- **[Context]**에 적절한 추천이 없을 경우, 빈 리스트를 반환하세요.

응답은 JSON 형식으로 **오직 추천된 콘텐츠의 asset_id의 리스트**만 포함해야 합니다.
{recommend_chain_format_instructions}
---
예제 출력 형식:
```json
{{"candidates": [1, 10, 31, 89, 135, 180]}}```
(만약 적절한 추천이 없을 경우)
```json
{{"candidates": []}}```

[사용자 입력과 사용자 입력값의 유형]:
{user_input}

[Context]:
{recommend_chain_retriever}

[Answer]:
"""
recommend_chain_prompt = ChatPromptTemplate.from_template(recommend_chain_template,
                                                          partial_variables={'recommend_chain_format_instructions': recommend_chain_format_instructions})
recommend_chain_llm = load_gemini()

# langchain 체인 구성
recommend_chain = (
  {"user_input":RunnablePassthrough(),
    "recommend_chain_retriever": multiquery_chain_retriever,
  }
  | recommend_chain_prompt               # 하나로 만든 문서를 prompt에 넘겨주고
  | recommend_chain_llm                  # llm이 원하는 답변을 만듦
  | output_parser
)