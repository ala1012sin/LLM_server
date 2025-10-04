from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import kakao_webhook
import uvicorn

# from contextlib import asynccontextmanager

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """애플리케이션 시작/종료 시 실행되는 이벤트"""
#     # ========== 시작 시 ==========
#     print("\n" + "="*80)
#     print("🚀 Application Starting...")
#     print("="*80 + "\n")
    
#     # Pinecone 테스트
#     try:
#         from services.pinecone_service import PineconeService
#         pinecone_service = PineconeService()
        
#         print("🔍 Testing Pinecone search...")
#         results = await pinecone_service.search_stores_by_text("테스트", top_k=1)
#         print(f"✅ Pinecone test completed: {len(results)} stores found\n")
        
#     except Exception as e:
#         print(f"❌ Pinecone test failed: {e}\n")
    
#     print("="*80)
#     print("✨ Application Ready!")
#     print("="*80 + "\n")
    
#     yield  # 여기서 애플리케이션 실행
    
#     # ========== 종료 시 ==========
#     print("\n👋 Application Shutting Down...\n")

app = FastAPI(
    title="Restaurant Chatbot API",
    description="카카오톡 맛집 추천 챗봇 API",
    version="1.0.0",
    # lifespan=lifespan  # lifespan 추가
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(kakao_webhook.router)

@app.get("/")
async def root():
    return {
        "message": "Restaurant Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "kakao_webhook": "/kakao/webhook",
            "health": "/kakao/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
