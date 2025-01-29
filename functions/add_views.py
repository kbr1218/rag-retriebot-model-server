# add_views.py
import datetime
from langchain_core.documents import Document
from fastapi import HTTPException
from setup import views_vectorstore, VECTORSTORE_PATH_VIEW_100

def add_view_to_vectorstore(user_id: str, asset_id: str, runtime: float):
    """
    사용자 시청기록에 새로운 값을 추가하는 함수
    Args:
        user_id (str): 사용자의 ID
        asset_id (str): VOD 콘텐츠의 ID
        runtime (float): VOD 콘텐츠의 런타임
    """
    try:
        # 시청기록 벡터스토어가 None일 경우
        if views_vectorstore is None:
            raise HTTPException(status_code=500, detail="벡터스토어가 로드되지 않음!")

        # 현재 시간
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 추가할 데이터 정의
        new_data = {
            "user_id": user_id,
            "asset_id": asset_id,
            "use_tms/runtime": 1,       # 사용자의 시청 시간을 알 수 없으므로 1로 고정
            "runtime": runtime,
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
        views_vectorstore.add_documents([doc])
        # 변경사항 저장
        views_vectorstore.save_local(VECTORSTORE_PATH_VIEW_100)

        return {"message": f"벡터스토어 저장 성공! ({user_id}, {asset_id})"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터스토어 저장 실패: {str(e)}")