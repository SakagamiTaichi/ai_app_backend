from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/token")


# サービスのインスタンス作成に依存性注入を使用
def get_chat_service() -> ChatService:
    return ChatService()


@router.get("/message")
async def chat_stream(
    message: str,
    session_id: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> StreamingResponse:
    """チャットのストリーミングレスポンスを取得する"""
    try:
        return StreamingResponse(
            chat_service.stream_response(message, session_id),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages")
async def chat_messages(
    token: Annotated[str, Depends(oauth2_scheme)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> None:
    """チャットの会話を保存する。"""
    try:
        # 現在のユーザー情報を取得
        # current_user = await auth_service.get_current_user(token)
        return await chat_service.save_conversation("user_id")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
