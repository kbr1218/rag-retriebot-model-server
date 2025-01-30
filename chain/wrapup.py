# wrapup.py
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from setup import load_template_from_yaml
from functions.fetch_movie_details import fetch_movie_details
from prompts.wrapup_response_schema import chatbot_response_schema, movie_detail_schema
from config import GEMINI_API_KEY, OPENAI_API_KEY


# movie와 chatbot schema 결합
output_parser = StructuredOutputParser.from_response_schemas(
    [movie_detail_schema, chatbot_response_schema]
)
wrapup_format_instructions = output_parser.get_format_instructions()

# template 불러오기
wrapup_template = load_template_from_yaml("./prompts/wrapup_template.yaml")
wrapup_prompt = ChatPromptTemplate.from_template(wrapup_template,
                                                 partial_variables={'wrapup_format_instructions': wrapup_format_instructions})


# LLM 모델 생성 (1. GEMINI 2. OpenAI)
def load_gemini():
    model = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0.3,
        max_tokens=5000,
        api_key=GEMINI_API_KEY
    )
    print(">>>>>>> Gemini loaded from wrap-up chain...")
    return model

def load_gpt():
    model = ChatOpenAI(
        model_name='gpt-4o-mini-2024-07-18',
        temperature=0,
        max_tokens=3000,
        api_key=OPENAI_API_KEY
    )
    print(">>>>>>> GPT loaded from wrap-up chain...")
    return model

wrapup_chain_llm = load_gemini()

# 영화 detail 가져오기
def process_wrapup_details(input_data):
    final_recommendations = input_data['final_recommendations']
    
    # asset_id 추출
    asset_ids = [movie['asset_id'] for movie in final_recommendations]
    movie_details = fetch_movie_details(asset_ids)

    movies_detail = []
    for movie in final_recommendations:
        asset_id = movie["asset_id"]
        reason = movie["reason"]
        details = movie_details.get(asset_id, None)

        # Append formatted data
        movies_detail.append({
            "asset_id": asset_id,
            "movie_id": details.metadata.get("movie_id", None) if details else None,
            "title": details.metadata.get("title", "Unknown Title") if details else "Unknown Title",
            "original_title": details.metadata.get("original_title", "N/A") if details else "N/A",
            "genre": details.metadata.get("genre", "N/A") if details else "N/A",
            "adult": details.metadata.get("adult", False) if details else False,
            "runtime": details.metadata.get("runtime", 0) if details else 0,
            "release_year": details.metadata.get("release_year", "N/A") if details else "N/A",
            "release_date": details.metadata.get("release_date", "N/A") if details else "N/A",
            "actors": details.metadata.get("actors", "N/A") if details else "N/A",
            "director": details.metadata.get("director", "N/A") if details else "N/A",
            "orgnl_cntry": details.metadata.get("orgnl_cntry", "N/A") if details else "N/A",
            "original_language": details.metadata.get("original_language", "N/A") if details else "N/A",
            "vote_average": details.metadata.get("vote_average", 0.0) if details else 0.0,
            "vote_count": details.metadata.get("vote_count", 0) if details else 0,
            "popularity": details.metadata.get("popularity", 0.0) if details else 0.0,
            "poster_path": details.metadata.get("poster_path", "N/A") if details else "N/A",
            "backdrop_path": details.metadata.get("backdrop_path", "N/A") if details else "N/A",
            "overview": details.page_content if details else "No description available.",
            "reason": reason
        })
    return {
        "movies_detail": movies_detail
    }


# langchain 체인 구성
wrapup_chain = (
    RunnablePassthrough()
  | process_wrapup_details
  | wrapup_prompt
  | wrapup_chain_llm
  | output_parser
)
