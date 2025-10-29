from fastapi import APIRouter, Request
import asyncio
import httpx
import uuid
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
    # TODO: 필요하면 유사도 기반 백업 로직 추가
    return None

@router.post("/store")
async def kakao_store(request: Request):
    body = await request.json()

    # ── 기본 추출 ──────────────────────────────────────────────────────────
    user_key = body.get("userRequest", {}).get("user", {}).get("id", "")
    utterance = (body.get("userRequest", {}).get("utterance") or "").strip()
    trigger_type = (body.get("flow", {}).get("trigger") or {}).get("type", "")
    extra = (body.get("action") or {}).get("clientExtra") or {}
    store_name = (extra.get("store_name") or "").strip()

    session = user_sessions.get(user_key)

    # ── 디버깅 로그 ───────────────────────────────────────────────────────
    print("==== /kakao/store IN ====")
    print("user_key:", user_key)
    print("trigger_type:", trigger_type)          # "CARD_BUTTON_BLOCK" / "TEXT_INPUT" 등
    print("utterance:", utterance)                # 버튼이면 "상세보기"가 들어올 수 있음(폰)
    print("store_name(extra):", store_name)       # 버튼에 실어 보낸 가게명
    print("session(before):", session)

    # ── 1) 상세보기(버튼) 진입 or 세션 미보유 → detail 모드로 전환 ───────
    #  - 폰에선 버튼 클릭해도 utterance="상세보기"가 들어올 수 있으므로
    #    'utterance 유무'가 아니라 'store_name 유무'와 '세션 상태'로 판단한다.
    if (not session or session.get("mode") != "detail") and store_name:
        # 파인콘에서 가게 정보 1건 조회(실패 시 이름만 담아 캐시)
        try:
            stores = await pinecone_service.search_stores_by_text(store_name, top_k=1)
        except Exception as e:
            print("[WARN] pinecone search failed:", e)
            stores = []

        store_info = stores[0] if stores else {"name": store_name}

        # 세션 detail 모드로 전환
        user_sessions[user_key] = {
            "mode": "detail",
            "store": store_info,
            "chat_history": []
        }
        print("session(after -> detail init):", user_sessions[user_key])

        # 인사/진입 응답
        greet = f"안녕하세요! 😊 '{store_name}'입니다.\n무엇을 도와드릴까요?"
        return kakao_service.create_text_response(greet)

    # ── 2) 아직 detail 모드가 아닌데 store_name도 없음 → 안내 ───────────
    if not session or session.get("mode") != "detail":
        # 추천카드에서 상세보기를 누르지 않고 바로 들어온 케이스 방어
        return kakao_service.create_text_response(
            "어떤 가게를 보고 계신가요? 카드에서 ‘상세보기’를 눌러 들어와 주세요."
        )

    # ── 3) detail 모드에서 사용자 질문 처리 ─────────────────────────────
    store = session["store"]
    chat_history = session.get("chat_history", [])

    # 빈 발화 방지(버튼 라벨만 들어오거나 공백만 있을 때)
    if not utterance:
        return kakao_service.create_text_response("무엇을 도와드릴까요? (예: 영업시간 알려줘)")

    # 콜백 플로우 지원: 카카오가 전달한 callbackUrl이 있으면
    # 1) 즉시 useCallback:true를 반환 (5초 SLA 회피)
    # 2) 백그라운드에서 LLM을 호출해 callbackUrl로 최종 응답을 POST
    callback_url = body.get("userRequest", {}).get("callbackUrl") or body.get("userRequest", {}).get("callback_url")

    if callback_url:
        # 즉시 반환할 메시지(개발자 문서 예시를 따름)
        placeholder = ""

        # schedule background task to generate final reply and POST to callback_url
        task_id = str(uuid.uuid4())

        async def _generate_and_post_callback(cb_url: str, store_info: dict, user_msg: str, history: list, ukey: str, tid: str):
            try:
                # Generate reply (may take time)
                reply_text = await openai_service.generate_store_response(store_info, user_msg, history)

                # Update session chat history
                try:
                    h = user_sessions.get(ukey, {}).get("chat_history", [])
                    h.extend([
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": reply_text},
                    ])
                    if ukey in user_sessions:
                        user_sessions[ukey]["chat_history"] = h[-10:]
                except Exception as _:
                    print(f"[WARN] failed to update session chat_history for user={ukey}")

                # Build callback payload (skill response format) - user will see this
                payload = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {"simpleText": {"text": reply_text}}
                        ]
                    }
                }

                # POST to callback URL
                async with httpx.AsyncClient(timeout=15.0) as client:
                    r = await client.post(cb_url, json=payload)
                    if r.status_code >= 200 and r.status_code < 300:
                        print(f"[CALLBACK:{tid}] posted successfully to callbackUrl for user={ukey}")
                    else:
                        print(f"[CALLBACK:{tid}] callback POST returned status={r.status_code} body={r.text}")
            except Exception as e:
                print(f"[ERROR][CALLBACK:{tid}] failed to generate/post callback reply:", e)

        # fire-and-forget
        asyncio.create_task(_generate_and_post_callback(callback_url, store, utterance, chat_history, user_key, task_id))

        # return initial useCallback response (no template field when useCallback true, include data if desired)
        resp = {
            "version": "2.0",
            "useCallback": True,
            "data": {"text": placeholder}
        }
        return resp

    # LLM 호출 (룰/FAQ 선처리하고 싶으면 여기서 분기)
    try:
        reply = await openai_service.generate_store_response(store, utterance, chat_history)
    except Exception as e:
        print("[ERROR] openai_service.generate_store_response:", e)
        return kakao_service.create_text_response("답변 생성 중 오류가 발생했어요. 잠시 후 다시 시도해 주세요.")

    # 대화 히스토리 업데이트(최근 N개만 유지)
    chat_history.extend([
        {"role": "user", "content": utterance},
        {"role": "assistant", "content": reply},
    ])
    session["chat_history"] = chat_history[-10:]
    user_sessions[user_key] = session

    print("session(after reply):", user_sessions[user_key])
    print("==== /kakao/store OUT ====")

    return kakao_service.create_text_response(reply)