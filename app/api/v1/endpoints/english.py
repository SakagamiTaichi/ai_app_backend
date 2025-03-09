from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer

from app.dependencies.repositories import get_english_repository, get_auth_repository
from app.repositories.english_repository import EnglishRepository
from app.repositories.auth_repository import AuthRepository
from app.schemas.english_chat import ConversationSet, Message, ConversationSetCreate, MessageCreate, MessageTestResultSummary, MessageTestResultUserAnswerRequest
from app.services.english_chat_service import EnglishChatService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/english", tags=["english"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/token")

# サービスのインスタンス作成に依存性注入を使用
def get_english_chat_service(repository: Annotated[EnglishRepository, Depends(get_english_repository)]) -> EnglishChatService:
    return EnglishChatService(repository)

def get_auth_service(repository: Annotated[AuthRepository, Depends(get_auth_repository)]) -> AuthService:
    return AuthService(repository)

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
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> List[ConversationSet]:
    """ログインユーザーの会話セットの一覧を取得する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        # ユーザーIDに基づいて会話セットをフィルタリング
        return await chat_service.get_conversation_sets(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/message/{set_id}", response_model=List[Message])
async def get_messages(
    set_id: UUID,
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> List[Message]:
    """特定の会話セットに属するメッセージを取得する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        return await chat_service.get_messages(set_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/test_result", response_model=MessageTestResultSummary)
async def post_test_results(
    request: MessageTestResultUserAnswerRequest,
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> MessageTestResultSummary:
    """ログインユーザーのテスト結果を取得する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        return await chat_service.post_test_results(current_user.id,request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/conversation_sets", response_model=ConversationSet)
async def create_conversation_set(
    data: ConversationSetCreate,
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[EnglishChatService, Depends(get_english_chat_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> ConversationSet:
    """新しい会話セットを作成する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        return await chat_service.create_conversation_set(data.title, current_user.id)
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
    
