from fastapi import HTTPException, status

from app.features.auth.domain.auth_repository import AuthRepository
from app.features.auth.model.auth import Token, UserResponse

class AuthService:
    """認証サービスクラス"""
    
    def __init__(self, repository: AuthRepository):
        self.repository = repository
    
    async def signup(self, email: str, password: str) -> UserResponse:
        """ユーザー登録"""
        return await self.repository.signup(email, password)
    
    async def signin(self, email: str, password: str) -> Token:
        """ユーザーサインイン"""
        return await self.repository.signin(email, password)
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """トークンのリフレッシュ"""
        return await self.repository.refresh_token(refresh_token)
    
    async def get_current_user(self, token: str) -> UserResponse:
        """現在のユーザー情報を取得"""
        try:
            return await self.repository.get_current_user(token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証に失敗しました",
                headers={"WWW-Authenticate": "Bearer"},
            )