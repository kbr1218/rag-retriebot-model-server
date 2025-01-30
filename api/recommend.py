# recommend.py
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from setup import movies_vectorstore, load_template_from_yaml
from config import GEMINI_API_KEY, OPENAI_API_KEY

# StructuredOutputParser 사용
recommend_response_schemas = [
  ResponseSchema(name="candidates",
                 description="사용자의 입력에 맞게 추천할 VOD 콘텐츠의 asset_id 리스트. 예: ['cjc|M4721638LFOL80567201', 'cjc|M4721638LFOL90477201', 'cjc|M4721649KQOL98147201']")
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

# 검색기 생성
multiquery_chain_retriever = MultiQueryRetriever.from_llm(
    retriever = movies_vectorstore.as_retriever(
        search_type="similarity",   
        search_kwargs={"k": 10,              # 반환할 문서 수 (default: 4)
                      #  "fetch_k": 50,        # MMR 알고리즘에 전달할 문서 수
                      #  "lambda_mult": 0.8,   # 결과 다양성 조절 (default: 0.5),
                       }
    ),
    llm = load_gemini()
)

# template 불러오기
recommend_template = load_template_from_yaml("./prompts/recommend_template.yaml")
recommend_chain_prompt = ChatPromptTemplate.from_template(recommend_template,
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