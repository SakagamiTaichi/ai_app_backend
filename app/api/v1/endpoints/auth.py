from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.dependencies.repositories import get_auth_service
from app.schemas.auth import Token, UserCreate, UserResponse, LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/token")

# 現在のユーザーを取得するための依存性
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserResponse:
    """
    認証トークンからユーザー情報を取得する依存性関数
    """
    return await auth_service.get_current_user(token)


@router.post("/register", response_model=Token)
async def register(
    user: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """
    新規ユーザー登録
    """
    try:
        return await auth_service.register(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """
    ユーザーログイン
    """
    try:
        return await auth_service.login(login_data.email, login_data.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# OAuth2互換のトークンエンドポイント
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """
    OAuth2準拠のトークン取得エンドポイント
    """
    try:
        return await auth_service.login(form_data.username, form_data.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_user_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> UserResponse:
    """
    現在ログインしているユーザーの情報を取得
    """
    return current_user