<div align="center">
    <img src="https://github.com/kbr1218/react-retriebot-frontend/blob/main/public/img/title2.png">
</div>
<br>

# Retriebot - a RAG-based VOD Recommendation Chatbot
**: RAG 기반 VOD 추천 대화형 AI 챗봇 서비스 "리트리봇"**

<br>

## ✏ 리트리봇 소개
<div align='center'><strong>RetrieBot = 🐕Retriever + 🤖ChatBot</strong></div><br>

**🐕Retriever (리트리버)**: 사용자의 질문과 관련된 문서를 검색하는 **검색기**로 RAG 시스템의 전반적인 성능과 직결되는 중요한 과정. **retrieve**는 **되찾아오다**라는 뜻을 가진 단어.  
**🤖ChatBot (챗봇)**: 유저의 메시지에 응답하는 봇.

<br>

## 🛠 시스템 아키텍처
<div align="center">
    <img src="https://github.com/kbr1218/react-retriebot-frontend/blob/main/public/img/시스템아키텍처.png" width="800">
</div>

<br>

## 🎨 기술 스택
<div style="text-align: left;">
  <div style="margin: ; text-align: left;" "text-align: left;">
    <p><strong>FE: &nbsp;</strong>
      <img src="https://img.shields.io/badge/react-61DAFB?style=flat&logo=react&logoColor=white">
      <img src="https://img.shields.io/badge/javascript-F7DF1E?style=flat&logo=javascript&logoColor=white">
      <img src="https://img.shields.io/badge/figma-F24E1E?style=flat&logo=figma&logoColor=white">
    </p>
    <p><strong>BE: &nbsp;</strong>
      <img src="https://img.shields.io/badge/python-3776AB?style=flat&logo=python&logoColor=white">
      <img src="https://img.shields.io/badge/fastapi-009688?style=flat&logo=fastapi&logoColor=white">
      <img src="https://img.shields.io/badge/pydantic-E92063?style=flat&logo=pydantic&logoColor=white">
      <img src="https://img.shields.io/badge/postman-FF6C37?style=flat&logo=postman&logoColor=white">
    </p>
    <p><strong>AI: &nbsp;</strong>
      <img src="https://img.shields.io/badge/langchain-1C3C3C?style=flat&logo=langchain&logoColor=white">
      <img src="https://img.shields.io/badge/ChromaDB-f76144?style=flat&logo=Java&logoColor=white">
      <img src="https://img.shields.io/badge/huggingface-FFD21E?style=flat&logo=huggingface&logoColor=white">
      <img src="https://img.shields.io/badge/openai-412991?style=flat&logo=openai&logoColor=white">
      <img src="https://img.shields.io/badge/googlegemini-8E75B2?style=flat&logo=googlegemini&logoColor=white">
    </p>
    <p><strong>PREPROCESSING: &nbsp;</strong>
      <img src="https://img.shields.io/badge/tableau-999999?style=flat&logo=Java&logoColor=white">
      <img src="https://img.shields.io/badge/spotfire-004088?style=flat&logo=Java&logoColor=white">
    </p>
    <p><strong>COLLAB: &nbsp;</strong>
      <img src="https://img.shields.io/badge/github-181717?style=flat&logo=github&logoColor=white">
      <img src="https://img.shields.io/badge/notion-000000?style=flat&logo=notion&logoColor=white">
      <img src="https://img.shields.io/badge/slack-4A154B?style=flat&logo=slack&logoColor=white">
    </p>
  </div>
</div>

<br>

## 📝 주요 기능
1. **사용자 시청 기록 기반 top-5 영화 추천**  
   * 사용자 시청 기록을 활용하여 LightFM 알고리즘을 적용한 top-5 영화 추천  
   * 시청 시간 비율의 합(`sum(use_tms/runtime)`)을 선호도 지표로 사용하여 모델 학습 및 예측 점수 측정  
   <br>
2. **VOD 정보 검색**
   * 사용자의 질문에 대한 답변과 함께 VOD 콘텐츠의 상세 정보 제공
   * 셀프쿼리 검색기(SelfQueryRetriever)를 사용하여 사용자 입력값으로 생성된 메타데이터 필터를 통한 정확한 검색 가능    
   <br>
3. **VOD 추천 요청**
   * 사용자 입력값과 시청 기록을 바탕으로 VOD 콘텐츠 추천 및 추천 이유 출력
   * recommend chain과 post-recommend chain으로 구성
     * recommend chain: 사용자 입력값을 기반으로 추천 후보군 선정
     * post-recommend chain: 추천 후보군에서 시청 기록을 고려하여 최종 Top-5 콘텐츠 선정
   * 멀티쿼리 검색기(MultiQueryRetriever)를 사용하여 다양한 검색 결과 제공 가능  
   <br>
4. **VOD 시청 기록 저장**
   * 사용자가 VOD를 시청하면 해당 VOD 데이터를 벡터스토어에 저장  
   * VOD ID (assetID)와 재생 시간을 기록하여 향후 추천 시스템에 반영  

<br>

## 📺 서비스 화면
- 초기 화면
<div align='center'>
    <img src="https://github.com/kbr1218/react-retriebot-frontend/blob/main/public/img/서비스화면1.png" width="800">
</div>
<br><br>

- 정보 검색
<div align="center">
    <img src="https://github.com/kbr1218/react-retriebot-frontend/blob/main/public/img/서비스화면2.png" width="800">
    <img src="https://github.com/kbr1218/react-retriebot-frontend/blob/main/public/img/서비스화면3.png" width="800">
</div>
<br><br>

- 추천 요청
<div align="center">
    <img src="https://github.com/kbr1218/react-retriebot-frontend/blob/main/public/img/서비스화면4.png" width="800">
</div>
<br>

## ✅ 실행 방법
1. install dependencies  
   ```
   poetry install
   ```
2. set .env
   ```python
   # .env_example 참고
   ```
3. start the development sever  
   ```
   uvicorn main:app --reload host 0.0.0.0 --port 8000
   ```  

<br>

## 📂 link to
- [API SERVER repo](https://github.com/kbr1218/fastapi-retriebot-api-server)
- [FE repo](https://github.com/kbr1218/react-retriebot-frontend)

<br><br><hr>

### ✔️commit message convention ###
- **`[FEAT]`** : 새로운 기능 추가
- **`[FIX]`** : 버그/에러 수정
- **`[DOCS]`** : 문서 수정
- **`[STYLE]`** : 코드 포맷팅, 세미콜론 누락 등 (코드 변경이 없는 경우)
- **`[TEST]`** : 테스트 코드
- **`[CHORE]`** : 빌드/패키지 매니저 수정, production code와 무관한 부분 (e.g. .gitignore, build.gradle)
- **`[COMMENT]`** : 주석 추가 및 변경

<hr>
