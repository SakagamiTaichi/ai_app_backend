from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.dependencies.repositories import get_auth_repository
from app.domain.auth.auth_repository import AuthRepository
from app.model.auth.auth import Token, UserCreate, UserLogin, UserResponse
from app.services.auth.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/token")

# サービスのインスタンス作成に依存性注入を使用
def get_auth_service(repository: Annotated[AuthRepository, Depends(get_auth_repository)]) -> AuthService:
    return AuthService(repository)

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserResponse:
    """新規ユーザー登録"""
    return await auth_service.signup(user_data.email, user_data.password)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """OAuth2互換のトークン取得エンドポイント"""
    return await auth_service.signin(form_data.username, form_data.password)

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """ユーザーログイン"""
    return await auth_service.signin(user_data.email, user_data.password)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: Token,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """トークンのリフレッシュ"""
    return await auth_service.refresh_token(token.refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserResponse:
    """現在のユーザー情報を取得"""
    return await auth_service.get_current_user(token)