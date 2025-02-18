# add_views.py
import datetime
from langchain_core.documents import Document
from fastapi import HTTPException
import setup

def add_view_to_vectorstore(user_id: str, asset_id: str):
    """
    사용자 시청기록에 새로운 값을 추가하는 함수
    Args:
        user_id (str): 사용자의 ID
        asset_id (str): VOD 콘텐츠의 ID
    """
    # 시청기록 전역변수 불러오기
    try:
        if setup.views_vectorstore is None:
            setup.views_vectorstore = setup.load_views_vectorstore(user_id)
    
        # 현재 시간
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 이미 시청한 영화인지 확인
        existing_result = setup.views_vectorstore.similarity_search(
            query="",
            k=1,
            filter={"$and": [
                {"user_id": {"$eq": user_id}}, 
                {"asset_id": {"$eq": asset_id}}
            ]}
        )

        # 이미 시청했다면 업데이트
        if existing_result:
            existing_data = eval(existing_result[0].page_content) 
            updated_use_tms_runtime = existing_data.get("use_tms/runtime", 1) + 1

            # 새로 덮어씌울 데이터 생성
            updated_data = {
                "user_id": user_id,
                "asset_id": asset_id,
                "use_tms/runtime": updated_use_tms_runtime,
                "datetime": current_datetime
            }
            # 기존 문서 삭제 (where 조건 수정)
            setup.views_vectorstore.delete(
                where={"$and": [
                    {"user_id": {"$eq": user_id}}, 
                    {"asset_id": {"$eq": asset_id}}
                ]}
            )

            # 새 Document 생성 후 추가
            updated_doc = Document(
                page_content=str(updated_data),
                metadata={"user_id": user_id, "asset_id": asset_id}
            )
            setup.views_vectorstore.add_documents([updated_doc])
            setup.views_vectorstore.persist()

            print("\n>>>>>>>>> 시청기록 업데이트")
            return {"answer": "재감상! 영화 재밌게 보세요!🍿"}
        
        # 기존 데이터가 없다면 새로 추가
        else:
            # 추가할 데이터 정의
            new_data = {
                "user_id": user_id,
                "asset_id": asset_id,
                "use_tms/runtime": 1,       # 새로운 데이터이므로 1부터 시작
                "datetime": current_datetime
            }

            # Document 형식으로 변환
            doc = Document(
                page_content=str(new_data),
                metadata = {
                    "user_id": user_id,
                    "asset_id": asset_id,
                }
            )
            # 벡터스토어에 추가
            setup.views_vectorstore.add_documents([doc])
            # 변경사항 저장
            setup.views_vectorstore.persist()

            return {"answer": "제가 잘 추천했군요🍿!  \n  언제든 또 보고 싶은 영화가 있으면 말해주세요! 더 좋은 영화를 물어올게요!🦴"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터스토어 저장 실패: {str(e)}")