from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.dependencies.repositories import get_auth_repository, get_mail_repository
from app.domain.auth.auth_repository import AuthRepository
from app.domain.email.emai_repository import EmailRepository

from app.endpoint.auth.auth_model import (
    PasswordResetModel,
    PasswordResetRequestModel,
    PasswordResetResponse,
    SignUpRequestModel,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
    VerificationCodeRequest,
    VerificationCodeResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/token")


# サービスのインスタンス作成に依存性注入を使用
def get_auth_service(
    repository: Annotated[AuthRepository, Depends(get_auth_repository)],
    mailRepository: Annotated[EmailRepository, Depends(get_mail_repository)],
) -> AuthService:
    return AuthService(repository=repository, mailRepository=mailRepository)


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    user_data: SignUpRequestModel,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """新規ユーザー登録"""
    try:
        return await auth_service.signup(
            user_data.email, user_data.password, user_data.code
        )
    except Exception as e:
        raise e


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """OAuth2互換のトークン取得エンドポイント"""
    return await auth_service.signin(form_data.username, form_data.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """ユーザーログイン"""
    return await auth_service.signin(user_data.email, user_data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token: TokenResponse,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """トークンのリフレッシュ"""
    return await auth_service.refresh_token(token.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """現在のユーザー情報を取得"""
    return await auth_service.get_current_user(token)


@router.post("/send-verification-code", response_model=VerificationCodeResponse)
async def send_verification_code(
    request: VerificationCodeRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> VerificationCodeResponse:
    """認証コードを送信する"""
    result = await auth_service.send_verification_code(request.email)
    return result


@router.post("/password-reset-request", response_model=PasswordResetResponse)
async def request_password_reset(
    request: PasswordResetRequestModel,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> PasswordResetResponse:
    """パスワードリセット要求"""
    return await auth_service.request_password_reset(request.email)


@router.post("/password-reset", response_model=PasswordResetResponse)
async def reset_password(
    request: PasswordResetModel,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> PasswordResetResponse:
    """パスワードリセット実行"""
    return await auth_service.reset_password(request.token, request.new_password)
