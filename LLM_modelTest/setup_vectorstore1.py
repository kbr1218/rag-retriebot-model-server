# setup_vectorstore.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader

from langchain_community.vectorstores import Chroma

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

import pandas as pd

DB_PATH = './movie_4000_vectorstore'

### 01. CSV 파일에서 문서 로드 ###
loader = CSVLoader('data\movie_4000_preprocessed.csv', encoding='utf8')
docs = loader.load()
print(f"문서의 수: {len(docs)}")


### 02. pandas로 데이터프레임 칼럼명 가져오기
csv_path = 'data\movie_4000_preprocessed.csv'
df = pd.read_csv(csv_path, encoding='utf8')
colnames = df.columns


### 03. 메타데이터 추가 ###
docs = []
for _, row in df.iterrows():
  # 필요한 메타데이터 설정
  metadata = {
    'title': row['movie_title'],
    'genre': row['genre']
  }
  # 각 행의 데이터를 문서로 변환
  doc = Document(
    page_content=str(row.to_dict()),
    metadata=metadata
  )
  docs.append(doc)

print(f"문서의 수: {len(docs)}")
print('[메타데이터 예시]\n', docs[100].metadata)


### 04. 데이터 청크 나누기 ###
text_splitter = RecursiveCharacterTextSplitter(
  chunk_size=1200, chunk_overlap=0
)
splits = text_splitter.split_documents(docs)
print("split된 문서의 수:", len(splits))


### 05. 임베딩 모델 생성
embeddings = HuggingFaceEmbeddings(model_name='jhgan/ko-sroberta-multitask')


### 06. 벡터스토어 생성 ###
## Chroma
vectorstore = Chroma.from_documents(
  documents=splits,
  embedding=embeddings,
  persist_directory=DB_PATH,
)
print("벡터스토어 저장 완료!")