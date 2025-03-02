from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.dependencies.repositories import get_english_repository
from app.repositories.english_repository import EnglishRepository
from app.schemas.english_chat import ConversationSet, Message, ConversationSetCreate, MessageCreate
from app.services.english_chat_service import EnglishChatService

router = APIRouter(prefix="/english", tags=["english"])

# サービスのインスタンス作成に依存性注入を使用
def get_english_chat_service(repository: Annotated[EnglishRepository, Depends(get_english_repository)]) -> EnglishChatService:
    return EnglishChatService(repository)

@router.get("/chat")
async def chat_stream(
    message: str,
    session_id: str,
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)]
) -> StreamingResponse:
    """チャットのストリーミングレスポンスを取得する"""
    try:
        return StreamingResponse(
            chat_service.stream_response(message, session_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation_sets", response_model=List[ConversationSet])
async def get_conversation_sets(
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)]
) -> List[ConversationSet]:
    """会話セットの一覧を取得する"""
    try:
        return await chat_service.get_conversation_sets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/message/{set_id}", response_model=List[Message])
async def get_messages(
    set_id: UUID,
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)]
) -> List[Message]:
    """特定の会話セットに属するメッセージを取得する"""
    try:
        return await chat_service.get_messages(set_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation_sets", response_model=ConversationSet)
async def create_conversation_set(
    data: ConversationSetCreate,
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)]
) -> ConversationSet:
    """新しい会話セットを作成する"""
    try:
        return await chat_service.create_conversation_set(data.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message", response_model=Message)
async def create_message(
    data: MessageCreate,
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)]
) -> Message:
    """新しいメッセージを作成する"""
    try:
        return await chat_service.create_message(
            data.set_id,
            data.message_order,
            data.speaker_number,
            data.message_en,
            data.message_ja
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))