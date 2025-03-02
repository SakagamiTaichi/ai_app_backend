from abc import ABC, abstractmethod
from typing import Optional
from app.schemas.auth import UserCreate, UserResponse



class AuthRepository(ABC):
    """認証関連のリポジトリインターフェース"""
    
    @abstractmethod
    async def create_user(self, user: UserCreate) -> UserResponse:
        """新規ユーザーを作成する"""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """メールアドレスからユーザーを取得する"""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """IDからユーザーを取得する"""
        pass
    
    @abstractmethod
    async def verify_password(self, email: str, password: str) -> bool:
        """パスワードを検証する"""
        pass