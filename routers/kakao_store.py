from fastapi import APIRouter, Request
from typing import Dict, Any, List
from services.pinecone_service import PineconeService
from services.openai_service import OpenAIService
from services.kakao_service import KakaoService
from .session import user_sessions

router = APIRouter(prefix="/kakao", tags=["kakao-store"])
pinecone_service = PineconeService()
openai_service = OpenAIService()
kakao_service = KakaoService()

def _pick_store_by_name(name: str, stores: List[Dict[str, Any]]):
    if not name:
        return None
    name_norm = name.strip().lower()
    for s in stores:
        if (s.get("name") or "").strip().lower() == name_norm:
            return s
    # 이름 완전일치가 없으면 가장 비슷한 후보 1개
    # (간단 백업: 파인콘으로 1개 검색)
    return None

# 상세보기/가게대화 블록의 스킬 URL => /kakao/store 로 설정
@router.post("/store")
async def kakao_store(request: Request):
    body = await request.json()
    user_key = body.get("userRequest", {}).get("user", {}).get("id", "")
    utterance = (body.get("userRequest", {}).get("utterance") or "").strip()
    session = user_sessions.get(user_key)

    print(session)

    # 상세보기 버튼에서 넘어온 extra (가게 이름)
    extra = (body.get("action") or {}).get("clientExtra") or {}
    store_name = (extra.get("store_name") or "").strip()

    print(store_name)

    # 1) 진입 첫 호출: utterance가 비어있음 → 인사만 보내고 세션 설정
    if utterance and not session:
        if store_name:
            # pinecone에서 1건만 찾아 캐시(다음 턴에 LLM이 사용할 수 있도록)
            stores = await pinecone_service.search_stores_by_text(store_name, top_k=1)
            store_info = stores[0] if stores else {"name": store_name}

            user_sessions[user_key] = {
                "mode": "detail",
                "store": store_info,
                "chat_history": []
            }

        # (가게가 안 잡혀도 인사는 보냅니다)
        text = f"안녕하세요! 😊 '{store_name}'입니다.\n무엇을 도와드릴까요?"
        return kakao_service.create_text_response(text)

    # 2) 두 번째 이후 호출: 사용자가 질문을 함 → 세션의 가게로 답변 생성

    if not session or session.get("mode") != "detail":
        # 세션 없으면 방어적으로 기본 안내
        return kakao_service.create_text_response("어떤 가게를 보고 계신가요? ‘상세보기’를 눌러 들어와 주세요.")

    store = session["store"]
    chat_history = session.get("chat_history", [])

    # LLM 호출 (느리면 최대한 짧게, 또는 룰 기반으로 처리 후 LLM)
    reply = await openai_service.generate_store_response(store, utterance, chat_history)

    chat_history.extend([
        {"role": "user", "content": utterance},
        {"role": "assistant", "content": reply},
    ])
    session["chat_history"] = chat_history[-10:]
    user_sessions[user_key] = session

    return kakao_service.create_text_response(reply)