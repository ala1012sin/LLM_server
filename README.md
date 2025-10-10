# 📝 LLM 기반 카카오톡 맛집 추천 챗봇 API

이 프로젝트는 **FastAPI**를 기반으로 구축된 **카카오톡 챗봇 API 서버**입니다. 사용자의 위치와 음식 취향에 맞춰 맛집을 추천하고, 특정 가게에 대한 상세 정보를 제공하며 사용자와의 대화를 통해 질문에 답변하는 기능을 제공합니다.

주요 기술로는 **OpenAI**의 언어 모델을 활용하여 자연스러운 답변을 생성하고, **Pinecone** 벡터 데이터베이스를 통해 빠르고 정확한 가게 정보를 검색합니다.

## ✨ 주요 기능

  * **맛집 추천**: 사용자의 현재 위치 또는 특정 지역과 음식 종류를 기반으로 주변 맛집을 추천합니다.
  * **위치 기반 검색**: **카카오 로컬 API**를 사용하여 텍스트로 입력된 위치를 좌표로 변환하고, 이를 기반으로 근처 가게를 검색합니다.
  * **상세 정보 제공**: 사용자가 가게를 선택하면, 해당 가게의 주소, 연락처, 영업시간, 메뉴, 주차 정보 등 상세 정보를 담은 카카오톡 메시지를 생성합니다.
  * **LLM 기반 대화**: 특정 가게를 선택한 후에는 **OpenAI의 GPT 모델**을 활용하여 해당 가게의 챗봇처럼 사용자의 질문에 자연스럽게 답변합니다.
  * **세션 관리**: 사용자별로 대화 상태(추천 목록 보기, 특정 가게와 대화 중)와 대화 기록을 관리하여 연속적인 대화가 가능하도록 합니다.

## 🛠️ 기술 스택

  * **백엔드**: FastAPI, Uvicorn
  * **AI & 머신러닝**:
      * **OpenAI**: `text-embedding-3-small` 모델을 사용한 텍스트 임베딩 및 `GPT-4`를 활용한 질의응답 생성
      * **Pinecone**: 벡터 데이터베이스를 활용한 유사도 기반 가게 정보 검색
  * **API**: 카카오톡 채널 API, 카카오 로컬 API
  * **데이터 모델링**: Pydantic
  * **환경 변수 관리**: python-dotenv

## 📂 프로젝트 구조

```
.
├── main.py                 # FastAPI 앱의 메인 실행 파일
├── requirements.txt        # 프로젝트 의존성 목록
├── .env                    # (예시) 환경 변수 설정 파일
├── .gitignore              # Git 추적 제외 파일 목록
├── README.md               # 프로젝트 설명 파일
|
├── models
│   └── schemas.py          # Pydantic 데이터 모델 정의
|
├── routers
│   ├── kakao_recommend.py  # '가게 추천' 요청 처리 라우터
│   ├── kakao_store.py      # '가게 상세 대화' 요청 처리 라우터
│   └── session.py          # 사용자 세션 관리를 위한 인메모리 저장소
|
├── services
│   ├── openai_service.py   # OpenAI API 호출 서비스
│   ├── pinecone_service.py # Pinecone 벡터 DB 연동 서비스
│   └── kakao_service.py    # 카카오톡 응답 형식 및 API 유틸리티
|
└── utils
    └── config.py           # 환경 변수 로드 및 설정 관리
```

## 🚀 시작하기

### 1\. 사전 준비

  * Python 3.8 이상
  * OpenAI, Pinecone, Kakao API 키 발급

### 2\. 프로젝트 클론 및 설정

```bash
# 1. 저장소를 클론합니다.
git clone https://github.com/your-username/LLM_server.git
cd LLM_server

# 2. 가상 환경을 생성하고 활성화합니다.
python -m venv venv
source venv/bin/activate

# 3. 필요한 라이브러리를 설치합니다.
pip install -r requirements.txt
```

### 3\. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래 내용을 채워주세요.

```env
# .env

# OpenAI 설정
OPENAI_API_KEY="sk-..."
OPENAI_API_MODEL="gpt-4"

# Pinecone 설정
PINECONE_API_KEY="..."
PINECONE_INDEX="your-index-name"
PINECONE_REGION="us-west-1"

# Kakao 설정 (위치 기반 검색 시 필요)
KAKAO_REST_API_KEY="..."
```

### 4\. 서버 실행

```bash
# uvicorn을 사용하여 FastAPI 서버를 실행합니다.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 성공적으로 실행되면 `http://localhost:8000`에서 API 문서를 확인할 수 있습니다.

## 🌐 API 엔드포인트

  * `POST /kakao/recommend`: **가게 추천**을 위한 메인 엔드포인트입니다. 카카오톡 오픈빌더의 '추천/검색' 블록에서 이 URL을 스킬로 설정합니다.
  * `POST /kakao/store`: 특정 **가게와의 대화**를 처리하는 엔드포인트입니다. '상세보기' 버튼을 통해 가게가 선택된 후의 모든 사용자 발화를 처리합니다.
  * `GET /`: API 서버의 상태와 버전을 확인하는 헬스 체크 엔드포인트입니다.

## ☁️ 배포 정보

이 서버는 Azure 가상 머신(Ubuntu) 환경에서 `screen`과 `uvicorn`을 사용하여 24시간 운영되도록 설계되었습니다.

  * **세션 접속**: `screen -r llm`
  * **서버 실행**: `uvicorn main:app --host 0.0.0.0 --port 8000`
  * **백그라운드 유지**: `Ctrl + A` 누른 후 `D` 입력