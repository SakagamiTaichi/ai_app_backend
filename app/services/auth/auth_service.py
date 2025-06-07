from pydantic import ValidationError
from app.core.app_exception import BadRequestError
from app.domain.auth.auth_repository import AuthRepository
from app.domain.auth.login_information_value_object import LoginInformationValueObject
from app.domain.email.emai_repository import EmailRepository
from app.model.auth.auth import TokenResponse, UserResponse, VerificationCodeResponse


class AuthService:
    """認証サービスクラス"""

    def __init__(self, repository: AuthRepository, mailRepository: EmailRepository):
        self.dbRepository: AuthRepository = repository
        self.mailRepository: EmailRepository = mailRepository

    async def send_verification_code(self, email: str) -> VerificationCodeResponse:
        """認証コードを送信する"""
        try:
            code: str = await self.dbRepository.save_verification_code(email)
            success = await self.mailRepository.send_verification_code(email, code)
            if success:
                return VerificationCodeResponse(email=email)
            else:
                raise BadRequestError(detail="認証コードの送信に失敗しました。")
        except ValidationError as e:
            raise BadRequestError(detail=e.title)
        except Exception as e:
            raise

    async def signup(self, email: str, password: str, code: str) -> TokenResponse:
        """ユーザー登録"""
        try:
            entity = await self.dbRepository.signup(email, password, code)

            return TokenResponse(
                access_token=entity.access_token,
                refresh_token=entity.refresh_token.refresh_token,
                token_type=entity.token_type,
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

            valueObject = await self.dbRepository.signin(loginInfo)
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
            valueObject = await self.dbRepository.refresh_token(refresh_token)
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
            entity = await self.dbRepository.get_current_user(token)
            return UserResponse(
                id=entity.id, email=entity.email, is_active=entity.is_active
            )
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise
