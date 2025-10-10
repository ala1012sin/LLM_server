# 📝 BSH 가게 정보 수집 및 벡터 DB 연동 시스템

이 프로젝트는 **Streamlit**으로 제작된 웹 설문조사 애플리케이션입니다. 챗봇의 지식 베이스가 될 가게 정보를 효율적으로 수집하고, 수집된 데이터를 **OpenAI** 임베딩 모델을 통해 벡터로 변환한 뒤, **Pinecone** 벡터 데이터베이스에 저장하는 것을 목표로 합니다.

## ✨ 주요 기능

  * **웹 기반 설문 폼**: Streamlit을 사용하여 가게명, 주소, 영업시간, 메뉴 등 상세 정보를 입력받을 수 있는 사용자 친화적인 UI를 제공합니다.
  * **데이터 검증**: 필수 입력 항목이 누락되지 않았는지 확인하여 데이터의 무결성을 보장합니다.
  * **주소-좌표 변환**: **카카오 로컬 API**를 활용하여 입력된 주소를 위도와 경도 좌표로 자동 변환합니다.
  * **데이터 저장**:
    1.  설문조사를 통해 제출된 데이터는 고유 ID와 함께 `outputs` 폴더에 **JSON 파일**로 백업됩니다.
    2.  정제된 텍스트 데이터를 **OpenAI 임베딩 모델**(`text-embedding-3-small`)을 사용해 벡터로 변환합니다.
    3.  변환된 벡터와 가게의 메타데이터를 **Pinecone 벡터 데이터베이스**에 `upsert`하여 챗봇이 검색할 수 있도록 합니다.
  * **자동 인덱스 생성**: Pinecone에 지정된 이름의 인덱스가 없을 경우, 자동으로 생성하여 초기 설정의 번거로움을 줄여줍니다.

## 🛠️ 기술 스택

  * **웹 프레임워크**: Streamlit
  * **AI & 머신러닝**:
      * **OpenAI**: 텍스트 데이터 벡터화를 위한 임베딩 모델 활용
      * **Pinecone**: 벡터 검색 및 데이터 저장을 위한 서비리스 인덱스
  * **API**: 카카오 로컬 API (주소 검색)
  * **환경 변수 관리**: python-dotenv

## 📂 프로젝트 구조

```
.
├── survey.py               # Streamlit 앱의 메인 실행 파일
├── requirements.txt        # 프로젝트 의존성 목록
├── .env                    # (예시) API 키 등 환경 변수 설정 파일
├── .gitignore              # Git 추적 제외 파일 목록
├── README.md               # 프로젝트 설명 파일
└── outputs/                # 설문 결과가 저장되는 JSON 파일 폴더
```

## 🚀 시작하기

### 1\. 사전 준비

  * Python 3.8 이상
  * **API 키 발급**:
      * OpenAI API Key
      * Pinecone API Key
      * Kakao REST API Key

### 2\. 프로젝트 클론 및 설정

```bash
# 1. 저장소를 클론합니다.
git clone https://github.com/your-username/bsh_front_db.git
cd bsh_front_db

# 2. 가상 환경을 생성하고 활성화합니다.
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 필요한 라이브러리를 설치합니다.
pip install -r requirements.txt
```

### 3\. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래와 같이 발급받은 API 키를 입력하세요.

```env
# .env

# OpenAI API 키
OPENAI_API_KEY="sk-..."

# Pinecone API 키 및 인덱스 정보
PINECONE_API_KEY="..."
PINECONE_INDEX="business-chatbot-setting-database" # Pinecone 인덱스 이름 (변경 가능)
PINECONE_CLOUD="aws"                               # Pinecone 클라우드 환경
PINECONE_REGION="us-west-1"                        # Pinecone 리전

# Kakao REST API 키 (주소 -> 좌표 변환용)
KAKAO_REST_API_KEY="..."
```

### 4\. 애플리케이션 실행

아래 명령어를 터미널에 입력하여 Streamlit 웹 애플리케이션을 실행합니다.

```bash
streamlit run survey.py
```

명령어 실행 후 웹 브라우저에서 설문조사 페이지가 열리며, 정보를 입력하고 제출하여 데이터베이스에 정보를 추가할 수 있습니다.
