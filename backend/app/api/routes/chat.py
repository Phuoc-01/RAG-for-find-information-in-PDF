from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.rag_chain import rag_chain
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    document_ids: Optional[List[str]] = None
    session_id: Optional[str] = None
    history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    session_id: str
    timestamp: datetime
    has_context: bool

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Endpoint chat với RAG"""
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        session_id = request.session_id or str(uuid.uuid4())
        
        result = rag_chain.ask(
            question=request.message,
            document_ids=request.document_ids,
            history=request.history
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=session_id,
            timestamp=datetime.utcnow(),
            has_context=result["has_context"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Chat với streaming response (Server-Sent Events)"""
    # TODO: Implement streaming
    pass