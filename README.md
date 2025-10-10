LLM_server

카카오 오픈빌더용 FastAPI 서버.
Azure VM(Ubuntu)에서 uvicorn + screen으로 24시간 운영.

📦 주요 웹훅(엔드포인트)

POST /kakao/recommend : 가게 추천 응답

POST /kakao/store : 가게가 결정된 후, 해당 가게 전용 챗봇 응답

(옵션) GET /health : 헬스체크(있다면)

현재 서버 주소: http://20.210.192.6:8000

# 스크린에 접속
screen -r llm

# (세션 안에서) 서버 실행
cd LLM_server
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 세션에서 빠져나오기 (백그라운드 유지)
Ctrl + A  누르고  D


# 실행 중인 세션 목록
screen -ls