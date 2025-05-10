from abc import ABC, abstractmethod

from app.domain.auth.login_information_value_object import LoginInformationValueObject
from app.domain.auth.token_value_object import TokenValueObject
from app.domain.auth.user_entity import UserEntity


class AuthRepository(ABC):
    """認証機能のリポジトリインターフェース"""

    @abstractmethod
    async def signup(self, email: str, password: str) -> UserEntity:
        """新規ユーザーを登録する"""
        pass

    @abstractmethod
    async def signin(self, loginInfo: LoginInformationValueObject) -> TokenValueObject:
        """ユーザーをサインインさせる"""
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenValueObject:
        """リフレッシュトークンを使用して新しいアクセストークンを取得する"""
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> UserEntity:
        """ユーザー情報を取得する"""
        pass

    @abstractmethod
    async def get_current_user(self, access_token: str) -> UserEntity:
        """現在のユーザー情報を取得する"""
        pass
