# post_recommend.py
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from setup import load_template_from_yaml
from config import GEMINI_API_KEY, OPENAI_API_KEY


# StructuredOutputParser 사용
post_recommend_response_schemas = [
    ResponseSchema(
      name="final_recommendations",
      description="최종적으로 선정된 5개의 VOD 콘텐츠의 asset_id 리스트",
      type="list",
      items="string"
    ),
    ResponseSchema(
        name="response",
        description="추천된 영화를 설명하는 챗봇의 응답 메시지",
        type="string"
    )
]
output_parser = StructuredOutputParser.from_response_schemas(post_recommend_response_schemas)


# 출력 지시사항 파싱
post_recommend_format_instructions = output_parser.get_format_instructions()

# template 불러오기
post_recommend_template = load_template_from_yaml("./prompts/post_recommend_template.yaml")
post_recommend_prompt = ChatPromptTemplate.from_template(
    post_recommend_template,
    partial_variables={'post_recommend_format_instructions': post_recommend_format_instructions}
)

# LLM 모델 생성 (1. GEMINI 2. OpenAI)
def load_gemini():
    model = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0.3,
        max_tokens=5000,
        api_key=GEMINI_API_KEY
    )
    print(">>>>>>> Gemini loaded from post-recommend chain...")
    return model

def load_gpt():
    model = ChatOpenAI(
        model_name='gpt-4o-mini-2024-07-18',  #'gpt-4o-2024-08-06',    #'gpt-4o-mini-2024-07-18',
        temperature=0,
        max_tokens=3000,
        api_key=OPENAI_API_KEY
    )
    print(">>>>>>> GPT loaded from post-recommend chain...")
    return model

post_recommend_chain_llm = load_gpt()


# langchain 체인 구성
post_recommend_chain = (
  {"user_input": RunnablePassthrough(),
   "candidate_movies": RunnablePassthrough(),
   "watched_movies": RunnablePassthrough(),
   "user_preference": RunnablePassthrough()
  }
  | post_recommend_prompt
  | post_recommend_chain_llm
  | output_parser
)