from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict

from app.db.session import get_db, SessionLocal
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.core.deps import get_current_user
from app.services.embedding_service import EmbeddingService
from app.services.milvus_service import search_similar
from app.services.gemini_service import GeminiService

router = APIRouter()
embedding_service = EmbeddingService()
gemini_service = GeminiService()

@router.post("/chat/sessions", response_model=Dict)
def create_chat_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """새로운 채팅 세션을 생성합니다."""
    new_session = ChatSession(user_id=current_user.id, title="새로운 챗")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"id": new_session.id, "title": new_session.title}

@router.get("/chat/sessions", response_model=List[Dict])
def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """사용자의 모든 채팅 세션 목록을 조회합니다."""
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return [{"id": s.id, "title": s.title} for s in sessions]

@router.get("/chat/sessions/{session_id}", response_model=List[Dict])
def get_chat_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 채팅 세션의 메시지들을 조회합니다."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="채팅 세션을 찾을 수 없습니다.")
    
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return [{"role": m.role, "content": m.content} for m in messages]


@router.post("/chat/sessions/{session_id}")
def post_chat_message(
    session_id: int,
    message: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """사용자 메시지를 처리하고 AI의 답변을 스트리밍으로 반환합니다."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="채팅 세션을 찾을 수 없습니다.")

    # 1. 사용자 메시지를 DB에 저장
    user_message = ChatMessage(session_id=session.id, role="user", content=message)
    db.add(user_message)
    
    # 2. Milvus에서 관련 노트 검색
    _, query_embedding = embedding_service.process_text(message)
    # query_embedding은 2차원 리스트이므로 첫 번째 벡터만 사용
    search_results = search_similar("notes", query_embedding[0], top_k=3)
    
    context = ""
    if search_results:
        # search_similar는 content를 포함한 딕셔너리 리스트를 반환
        contents = [res['content'] for res in search_results if 'content' in res]
        context = "\n---\n".join(filter(None, contents))
    else:
        context = "관련 정보를 찾지 못했습니다."

    # 3. 이전 대화 기록 불러오기
    history = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    # 4. Gemini API 호출 및 스트리밍 응답 생성
    def stream_response(session_id_for_stream: int):
        full_response = ""
        db_stream = SessionLocal()
        try:
            for chunk in gemini_service.generate_chat_response(history_dicts, message, context):
                full_response += chunk
                yield chunk

            # 5. AI 응답을 DB에 저장 (스트림이 끝난 후)
            if full_response.strip():
                assistant_message = ChatMessage(session_id=session_id_for_stream, role="assistant", content=full_response)
                db_stream.add(assistant_message)
                db_stream.commit()
        finally:
            db_stream.close()

    db.commit() # 사용자 메시지를 먼저 커밋
    return StreamingResponse(stream_response(session.id), media_type="text/plain") 