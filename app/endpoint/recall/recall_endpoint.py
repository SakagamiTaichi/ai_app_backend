from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.dependencies.repositories import (
    get_auth_repository,
    get_english_recall_repository,
    get_mail_repository,
)
from app.domain.auth.auth_repository import AuthRepository
from app.domain.email.emai_repository import EmailRepository
from app.domain.recall.recall_card_repository import RecallCardrepository
from app.endpoint.recall.recall_model import (
    NextRecallCardResponse,
    RecallCardAnswerRequest,
)
from app.services.auth_service import AuthService
from app.services.recall_card_service import RecallCardService


router = APIRouter(prefix="/recall", tags=["recall"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/token")


# サービスのインスタンス作成に依存性注入を使用
def get_service(
    dbRepository: Annotated[
        RecallCardrepository, Depends(get_english_recall_repository)
    ],
) -> RecallCardService:
    return RecallCardService(dbRepository)


def get_auth_service(
    repository: Annotated[AuthRepository, Depends(get_auth_repository)],
    mailRepository: Annotated[EmailRepository, Depends(get_mail_repository)],
) -> AuthService:
    return AuthService(repository, mailRepository)


@router.get("/get_next_recall_card", response_model=NextRecallCardResponse)
async def get_next_reacall_card(
    token: Annotated[str, Depends(oauth2_scheme)],
    recall_card_service: Annotated[RecallCardService, Depends(get_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> NextRecallCardResponse:
    """ログインユーザーの会話セットの一覧を取得する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        # ユーザーIDに基づいて会話セットをフィルタリング
        return await recall_card_service.get_next_recall_card(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer_recall_card")
async def answer_recall_card(
    token: Annotated[str, Depends(oauth2_scheme)],
    recall_card_service: Annotated[RecallCardService, Depends(get_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    recall_card_answer_request: RecallCardAnswerRequest,
):
    """暗記カードの回答を処理する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        # ユーザーIDに基づいて回答を処理
        await recall_card_service.update_recall_card(
            current_user.id, recall_card_answer_request
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
