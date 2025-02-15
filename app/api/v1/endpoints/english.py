from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.english_chat import  ConversationSet, Message
from app.services.english_chat_service import EnglishChatService
router = APIRouter(prefix="/english", tags=["english"])
chat_service = EnglishChatService()


@router.get("/chat")
async def chat_stream(message: str,session_id : str) -> StreamingResponse:
    try:
        return StreamingResponse(
            chat_service.stream_response(message,session_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/conversation_sets")
async def get_conversation_sets() -> List[ConversationSet]:
    try:
        return chat_service.get_conversation_sets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/message/{set_id}")
async def get_messages(set_id: str) -> List[Message]:
    try:
        return chat_service.get_messages(set_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))