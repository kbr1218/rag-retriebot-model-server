# filter_watched_content.py
from functions.is_watched import is_watched

def filter_watched_contents(user_id: str, candidate_asset_ids: list):
  """
  후보로 선택 VOD 중 사용자가 이미 시청한 VOD는 제거하는 함수

  Args:
    user_id (str): 사용자 ID
    candidate_asset_ids (list): 후보 VOD의 asset_id가 들어있는 리스트

  Returns:
    list: 사용자가 시청하지 않은 VOD 후보들의 리스트
  """
  return [asset_id for asset_id in candidate_asset_ids
          if not is_watched(user_id, asset_id)]