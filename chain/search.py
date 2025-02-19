# search.py
from langchain.chains.query_constructor.base import AttributeInfo, StructuredQueryOutputParser, get_query_constructor_prompt
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from setup import movies_vectorstore
from config import OPENAI_API_KEY, GEMINI_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOpenAI
from setup import load_template_from_yaml

metadata_field_info = [
    AttributeInfo(
        name="asset_id",
        description="The unique identifier for a VOD (Video On Demand) asset, used for content retrieval and metadata linking.",
        type="string"
    ),
    AttributeInfo(
        name="title",
        description="The official title of the VOD content, typically used for display and user search.",
        type="string"
    ),
    AttributeInfo(
        name="original_title",
        description="The original title of the VOD content, often in its native language or as released in the country of origin.",
        type="string"
    ),
    AttributeInfo(
        name="genre",
        description="A comma-separated list of genres associated with the VOD content (e.g., 'SF, Horror, Drama'). "
                    "This allows content to be classified under multiple categories, enabling better search and recommendation.",
        type="string"
    ),
    AttributeInfo(
        name="adult",
        description="Indicates whether the content is for adults only. Accepts values: True (adult content), False (not adult content), or NaN (unknown).",
        type="boolean"
    ),
    AttributeInfo(
        name="runtime",
        description="The duration of the movie in minutes, used for filtering based on movie length.",
        type="float"
    ),
    AttributeInfo(
        name="release_year",
        description="The release year of the movie.",
        type="float"
    ),
    AttributeInfo(
        name="release_month",
        description="The release month of the movie.",
        type="float"
    ),
    AttributeInfo(
        name="release_day",
        description="The release day of the movie.",
        type="float"
    ),
    AttributeInfo(
        name="actors",
        description="A comma-separated list of main cast members (e.g., '송강호, 변희봉, 박해일').",
        type="string"
    ),
    AttributeInfo(
        name="director",
        description="A comma-separated list of directors if multiple (e.g., '봉준호').",
        type="string"
    ),
    AttributeInfo(
        name="orgnl_cntry",
        description="The country of origin of the movie.",
        type="string"
    ),
    AttributeInfo(
        name="original_language",
        description="The primary language of the movie (e.g., 'ko' for Korean, 'en' for English).",
        type="string"
    ),
    AttributeInfo(
        name="vote_average",
        description="The average rating of the movie, ranging from 0 to 10.",
        type="float"
    ),
    AttributeInfo(
        name="vote_count",
        description="The total number of user ratings received for the movie.",
        type="float"
    ),
    AttributeInfo(
        name="popularity",
        description="A score representing how popular the movie is based on user interactions.",
        type="float"
    )
]



document_content_description = "This document represents an individual entry in a movie information database. Each document contains metadata about a movie, including its title, original title, genre, director, actors, release year, runtime, country of origin, language, rating, popularity score, and more. Additionally, a synopsis of the movie is provided."

def load_gemini():
    model = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0.3,
        api_key=GEMINI_API_KEY
    )
    print(">>>>>>> Gemini loaded from search chain...")
    return model

def load_gpt():
    model = ChatOpenAI(
        model_name='gpt-4o-mini-2024-07-18',
        temperature=0,
        api_key=OPENAI_API_KEY
    )
    print(">>>>>>> GPT loaded from search chain...")
    return model

llm = load_gpt()

prompt = get_query_constructor_prompt(
    document_contents = document_content_description,  # 문서 내용 설명
    attribute_info  = metadata_field_info  # 메타데이터 필드 정보
)

class CustomChromaTranslator(ChromaTranslator):
    def visit_comparison(self, comparison):
        """Ensure numerical fields are cast to float for Chroma filtering, and support string filtering."""
        field_name = comparison.attribute
        value = comparison.value

        # 변환해야 하는 필드 리스트
        float_fields = ["release_year", "release_month", "release_day"]
        string_fields = ["genre", "actors", "director", "title", "original_title"]

        if field_name in float_fields:
            value = float(value)  # float 변환
            return {field_name: {f"${comparison.comparator.value}": value}}

        elif field_name in string_fields:
            # 문자열 필터링 방식: `$contains` → `$in`
            if comparison.comparator.value == "contain":
                return {field_name: {"$in": [value]}}  # `$contains` 대신 `$in` 사용

        # 기본 처리
        return {field_name: {f"${comparison.comparator.value}": value}}



# StructuredQueryOutputParser 를 생성
output_parser = StructuredQueryOutputParser.from_components()
# query_constructor chain 을 생성
query_constructor = prompt | llm | output_parser



retriever = SelfQueryRetriever(
    query_constructor=query_constructor,  # 이전에 생성한 query_constructor chain 을 지정
    vectorstore=movies_vectorstore,  # 벡터 저장소를 지정
    enable_limit=True,
    search_kwargs={"k": 20},
    structured_query_translator=CustomChromaTranslator(),  # 쿼리 변환기
)

search_response_schemas = [
  ResponseSchema(
      name="asset_id",
      description="VOD 콘텐츠의 ID 리스트, 최대 5개의 asset_id만 포함합니다.",
      type="list"
      ),
  ResponseSchema(
      name="answer",
      description="VOD를 통해 질문에 대한 답변, 한국어이면서 존댓말 구어체로 답변합니다. 최대 5개의 asset_id만 포함되기 때문에 reason도 최대 5개의 reason만 포함합니다.",
      type="string"
      )
]

output_parser = StructuredOutputParser.from_response_schemas(search_response_schemas)
# 출력 지시사항 파싱
search_format_instructions = output_parser.get_format_instructions()

# template 불러오기
search_template = load_template_from_yaml("./prompts/search_template.yaml")
search_prompt = ChatPromptTemplate.from_template(
    search_template,
    partial_variables={'search_format_instructions': search_format_instructions}
)

search_chain = (
    {
      "user_input": RunnablePassthrough(),
      "Self_Query_Retriever": retriever,
    }
    | search_prompt
    | llm
    | output_parser
)