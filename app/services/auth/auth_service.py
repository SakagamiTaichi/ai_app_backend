from pydantic import ValidationError
from app.core.app_exception import BadRequestError
from app.domain.auth.auth_repository import AuthRepository
from app.domain.auth.login_information_value_object import LoginInformationValueObject
from app.model.auth.auth import TokenResponse, UserResponse


class AuthService:
    """認証サービスクラス"""

    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def signup(self, email: str, password: str) -> UserResponse:
        """ユーザー登録"""
        try:
            entity = await self.repository.signup(email, password)

            return UserResponse(
                id=entity.id, email=entity.email, is_active=entity.is_active
            )
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise

    async def signin(self, email: str, password: str) -> TokenResponse:
        """ユーザーサインイン"""
        try:
            # ログイン情報バリューオブジェクトに変換
            loginInfo = LoginInformationValueObject(email=email, password=password)

            valueObject = await self.repository.signin(loginInfo)
            return TokenResponse(
                access_token=valueObject.access_token,
                refresh_token=valueObject.refresh_token.refresh_token,
                token_type=valueObject.token_type,
            )
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """トークンのリフレッシュ"""
        try:
            valueObject = await self.repository.refresh_token(refresh_token)
            return TokenResponse(
                access_token=valueObject.access_token,
                refresh_token=valueObject.refresh_token.refresh_token,
                token_type=valueObject.token_type,
            )
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise

    async def get_current_user(self, token: str) -> UserResponse:
        """現在のユーザー情報を取得"""
        try:
            entity = await self.repository.get_current_user(token)
            return UserResponse(
                id=entity.id, email=entity.email, is_active=entity.is_active
            )
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise
