from app.domain.auth.auth_repository import AuthRepository
from app.model.auth.auth import Token, UserResponse

class AuthService:
    """認証サービスクラス"""
    
    def __init__(self, repository: AuthRepository):
        self.repository = repository
    
    async def signup(self, email: str, password: str) -> UserResponse:
        """ユーザー登録"""
        try:
            return await self.repository.signup(email, password)
        except Exception as e:
            raise
    
    async def signin(self, email: str, password: str) -> Token:
        """ユーザーサインイン"""
        try:
            return await self.repository.signin(email, password)
        except Exception as e:
            raise
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """トークンのリフレッシュ"""
        try:
            return await self.repository.refresh_token(refresh_token)
        except Exception as e:
            raise
    
    async def get_current_user(self, token: str) -> UserResponse:
        """現在のユーザー情報を取得"""
        try:
            return await self.repository.get_current_user(token)
        except Exception as e:
            raise