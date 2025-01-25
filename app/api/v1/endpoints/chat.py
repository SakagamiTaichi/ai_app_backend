import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import RagChatService
import json

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = RagChatService()

@router.get("/stream")
async def chat_stream(message: str) -> StreamingResponse:
    try:
        return StreamingResponse(
            chat_service.stream_response(message),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))