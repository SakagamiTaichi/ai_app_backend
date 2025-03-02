from abc import ABC, abstractmethod
from app.schemas.auth import Token, UserResponse

class AuthRepository(ABC):
    """認証機能のリポジトリインターフェース"""
    
    @abstractmethod
    async def signup(self, email: str, password: str) -> UserResponse:
        """新規ユーザーを登録する"""
        pass
    
    @abstractmethod
    async def signin(self, email: str, password: str) -> Token:
        """ユーザーをサインインさせる"""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Token:
        """リフレッシュトークンを使用して新しいアクセストークンを取得する"""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: str) -> UserResponse:
        """ユーザー情報を取得する"""
        pass
    
    @abstractmethod
    async def get_current_user(self, access_token: str) -> UserResponse:
        """現在のユーザー情報を取得する"""
        pass