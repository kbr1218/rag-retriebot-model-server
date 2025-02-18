# LightFM.py
import pandas as pd
import numpy as np
import heapq
from functions.fetch_movie_details import fetch_movie_details
import os

def provide_score(loaded_model, userid, user_history_data):
  print(os.getcwd())

  # LightFM 사용할 컬럼 user_ids, asset_ids 로드
  user_ids = pd.read_csv("./db/user_mapping.csv")
  asset_ids = pd.read_csv("./db/asset_mapping.csv")

  # post로 받은 userid를 쿼리하기 위해 DataFrame으로 변환
  user_df = pd.DataFrame(user_ids)
  user_index = user_df.query("user_id == @userid")["user_index"].values[0]
  print(user_index)
  
  # 모든 아이템에 대한 예측 점수 계산
  scores = loaded_model.predict(int(user_index), np.array(asset_ids["asset_index"]))
  print(f"{scores} LightFM 추천 완료!")

  # 결과를 DataFrame으로 정리
  df_recommendations = pd.DataFrame({
    "asset_id": asset_ids["asset_id"],
    "asset_index": asset_ids["asset_index"],
    "score": scores
    }).sort_values(by="score", ascending=False)
  
  user_data_score_cache = df_recommendations.set_index("asset_id")["score"].to_dict()

  # 시청한 asset_id list에 담기
  watched_movies_asset_ids = set([doc.metadata["asset_id"] for doc in user_history_data[userid]])

  # LLM 리스트에서 존재하는 영화만 필터링 후, heap을 사용하여 5개만 유지
  top_5_movies = heapq.nlargest(
      5,  # 5개 선택
      [(movie, user_data_score_cache[movie]) for movie in user_data_score_cache if movie not in watched_movies_asset_ids],  # 필터링된 영화 리스트
      key=lambda x: x[1]  # 점수 기준 정렬
  )
  
  top_5_movies = ([tup[0] for tup in top_5_movies])
  default_5_movies = fetch_movie_details(top_5_movies)
  return default_5_movies