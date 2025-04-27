from supabase import Client
from app.core.exception.app_exception import InternalServerError
from app.domain.auth.auth_repository import AuthRepository
from app.domain.auth.login_information_value_object import LoginInformationValueObject
from app.domain.auth.refresh_token_value_object import RefreshTokenValueObject
from app.domain.auth.token_value_object import TokenValueObject
from app.domain.auth.user_entity import UserEntity
from app.exception.auth.auth_exception import AuthenticationException, FailedToCreateUserException
from fastapi import HTTPException, status

class AuthSupabaseRepository(AuthRepository):
    """Supabaseを使用した認証リポジトリの実装"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def signup(self, email: str, password: str) -> UserEntity:
        """新規ユーザーを登録する"""
        try:
            # Supabaseの認証APIを使用してユーザーを登録
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # ユーザー情報を返す
            user_data = response.user
            if not user_data:
                raise FailedToCreateUserException()
            
            if not user_data.email:
                raise FailedToCreateUserException()
            
            return UserEntity(
                id=user_data.id,
                email=user_data.email,
                is_active=not user_data.email_confirmed_at is None
            )
            
        except Exception as e:
            raise InternalServerError()
    
    async def signin(self, loginInfo:LoginInformationValueObject) -> TokenValueObject:
        """ユーザーをサインインさせる"""
        try:

            # Supabaseの認証APIを使用してサインイン
            response = self.client.auth.sign_in_with_password({
                "email": loginInfo.email,
                "password": loginInfo.password
            })
            
            session = response.session
            if not session:
                raise AuthenticationException()
            
            # トークン情報を返す
            return TokenValueObject(
                access_token=session.access_token,
                refresh_token=RefreshTokenValueObject(refresh_token=session.refresh_token),
                token_type="bearer"
            )
            
        except Exception as e:
            raise InternalServerError()
    
    async def refresh_token(self, refresh_token: str) -> TokenValueObject:
        """リフレッシュトークンを使用して新しいアクセストークンを取得する"""
        try:
            # Supabaseの認証APIを使用してトークンをリフレッシュ
            response = self.client.auth.refresh_session(refresh_token)
            
            session = response.session
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="トークンのリフレッシュに失敗しました"
                )
            
            # 新しいトークン情報を返す
            return TokenValueObject(
                access_token=session.access_token,
                refresh_token=RefreshTokenValueObject(refresh_token=session.refresh_token),
                token_type="bearer"
            )
            
        except Exception as e:
            # エラーハンドリング
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"トークンリフレッシュエラー: {str(e)}"
            )
    
    async def get_user(self, user_id: str) -> UserEntity:
        """ユーザー情報を取得する"""
        try:
            # Supabaseからユーザー情報を取得
            response = self.client.auth.admin.get_user_by_id(user_id)
            
            user_data = response.user
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ユーザーが見つかりません"
                )
            
            if not user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ユーザーが見つかりません"
                )
            
            return UserEntity(
                id=user_data.id,
                email=user_data.email,
                is_active=not user_data.email_confirmed_at is None
            )
            
        except Exception as e:
            # エラーハンドリング
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ユーザー情報取得エラー: {str(e)}"
            )
    
    async def get_current_user(self, access_token: str) -> UserEntity:
        try:
            # Supabaseの認証APIを使用してトークンを検証
            user = self.client.auth.get_user(access_token)
        
            if not user or not user.user.id or not user.user.email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="無効なトークンです"
                )
            
            # ユーザー情報を返す
            return UserEntity(
                id=user.user.id,
                email=user.user.email,
                is_active=not user.user.email_confirmed_at is None
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"認証エラー: {str(e)}"
            )