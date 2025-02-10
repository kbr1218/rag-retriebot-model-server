# is_watched.py
import setup

def is_watched(user_id: str, asset_id: str) -> bool:
    """
    views_vectorstore에서 사용자의 특정 asset_id 시청 여부 확인
    
    Args:
      user_id (str): 사용자 ID
      asset_id (str): 조회할 asset ID

    Returns:
      bool: 시청했다면 True, 시청하지 않았다면 False
    """
    if setup.views_vectorstore is None:
        print("🔄 벡터스토어가 None임 새로 로드 (is_watched.py)")
        print(f"------------------여기: {user_id}")
        setup.views_vectorstore = setup.load_views_vectorstore(user_id)
    
    watched_results = setup.views_vectorstore.similarity_search(
      query="",
      k=1,
      filter={"$and": [
          {"user_id": {"$eq": user_id}}, 
          {"asset_id": {"$eq": asset_id}}
      ]}
    )
    
    return len(watched_results) > 0