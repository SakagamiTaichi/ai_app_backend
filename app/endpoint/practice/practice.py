from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from app.core.dependencies.repositories import get_auth_repository, get_english_repository
from app.domain.auth.auth_repository import AuthRepository
from app.domain.practice.practice_repository import PracticeRepository
from app.services.auth.auth_service import AuthService
from app.model.practice.practice import Conversation, ConversationsResponse, ConversationSetCreate, Message, MessageCreate, MessageTestResultSummary, RecallTestRequest
from app.services.practicce.practice_service import PracticeService

router = APIRouter(prefix="/practice", tags=["practice"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/token")

# サービスのインスタンス作成に依存性注入を使用
def get_english_chat_service(repository: Annotated[PracticeRepository, Depends(get_english_repository)]) -> PracticeService:
    return PracticeService(repository)

def get_auth_service(repository: Annotated[AuthRepository, Depends(get_auth_repository)]) -> AuthService:
    return AuthService(repository)

@router.get("/chat")
async def chat_stream(
    message: str,
    session_id: str,
    chat_service: Annotated[PracticeService, Depends(get_english_chat_service)]
) -> StreamingResponse:
    """チャットのストリーミングレスポンスを取得する"""
    try:
        return StreamingResponse(
            chat_service.stream_response(message, session_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations", response_model=ConversationsResponse)
async def get_conversations(
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[PracticeService, Depends(get_english_chat_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> ConversationsResponse:
    """ログインユーザーの会話セットの一覧を取得する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        # ユーザーIDに基づいて会話セットをフィルタリング
        return await chat_service.get_conversations(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}", response_model=List[Message])
async def get_conversation(
    conversation_id: UUID,
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[PracticeService, Depends(get_english_chat_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> List[Message]:
    """特定の会話を取得する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        return await chat_service.get_conversation(conversation_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/test_result", response_model=MessageTestResultSummary)
async def post_test_results(
    request: RecallTestRequest,
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[PracticeService, Depends(get_english_chat_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> MessageTestResultSummary:
    """ログインユーザーのテスト結果を取得する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        return await chat_service.post_test_results(current_user.id,request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/conversation", response_model=Conversation)
async def create_conversations(
    data: ConversationSetCreate,
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[PracticeService, Depends(get_english_chat_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Conversation:
    """新しい会話を作成する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        return await chat_service.create_conversation_set(data.title, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message", response_model=Message)
async def create_message(
    data: MessageCreate,
    chat_service: Annotated[PracticeService, Depends(get_english_chat_service)]
) -> Message:
    """新しいメッセージを作成する"""
    try:
        return await chat_service.create_message(
            data.conversation_id,
            data.message_order,
            data.speaker_number,
            data.message_en,
            data.message_ja
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
