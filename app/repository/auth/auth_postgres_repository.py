from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import SecurityUtils
from app.domain.auth.auth_repository import AuthRepository
from app.domain.auth.login_information_value_object import LoginInformationValueObject
from app.domain.auth.refresh_token_value_object import RefreshTokenValueObject
from app.domain.auth.token_value_object import TokenValueObject
from app.domain.auth.user_entity import UserEntity
from app.schema.auth.user_model import UserModel
from app.exception.auth.auth_exception import (
    AuthenticationException,
    FailedToCreateUserException,
    UserAlreadyExistsException,
)
from fastapi import HTTPException, status


class AuthPostgresRepository(AuthRepository):
    """PostgreSQLを使用した認証リポジトリの実装"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def signup(self, email: str, password: str) -> UserEntity:
        """新規ユーザーを登録する"""
        try:
            # 既存ユーザーのチェック
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )

            existing_user = result.scalar_one_or_none()

            if existing_user:
                raise UserAlreadyExistsException(email)

            # パスワードのハッシュ化
            hashed_password = SecurityUtils.get_password_hash(password)

            # 新規ユーザーの作成
            new_user = UserModel(
                email=email, hashed_password=hashed_password, is_active=True
            )

            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            return UserEntity(
                id=str(new_user.id),
                email=str(new_user.email),
                is_active=bool(new_user.is_active),
            )

        except UserAlreadyExistsException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise FailedToCreateUserException()

    async def signin(self, loginInfo: LoginInformationValueObject) -> TokenValueObject:
        """ユーザーをサインインさせる"""
        try:
            # ユーザーの取得
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == loginInfo.email)
            )
            user = result.scalar_one_or_none()

            if not user or not SecurityUtils.verify_password(
                loginInfo.password, str(user.hashed_password)
            ):
                raise AuthenticationException()

            # トークンの生成
            access_token = SecurityUtils.create_access_token({"sub": str(user.id)})
            refresh_token = SecurityUtils.create_refresh_token({"sub": str(user.id)})

            return TokenValueObject(
                access_token=access_token,
                refresh_token=RefreshTokenValueObject(refresh_token=refresh_token),
                token_type="bearer",
            )

        except AuthenticationException:
            raise
        except Exception as e:
            raise AuthenticationException()

    async def refresh_token(self, refresh_token: str) -> TokenValueObject:
        """リフレッシュトークンを使用して新しいアクセストークンを取得する"""
        try:
            payload = SecurityUtils.decode_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="無効なリフレッシュトークンです",
                )

            user_id = payload.get("sub")

            # 新しいトークンの生成
            access_token = SecurityUtils.create_access_token({"sub": user_id})
            new_refresh_token = SecurityUtils.create_refresh_token({"sub": user_id})

            return TokenValueObject(
                access_token=access_token,
                refresh_token=RefreshTokenValueObject(refresh_token=new_refresh_token),
                token_type="bearer",
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"トークンリフレッシュエラー: {str(e)}",
            )

    async def get_user(self, user_id: str) -> UserEntity:
        """ユーザー情報を取得する"""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ユーザーが見つかりません",
                )

            return UserEntity(
                id=str(user.id), email=str(user.email), is_active=bool(user.is_active)
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ユーザー情報取得エラー: {str(e)}",
            )

    async def get_current_user(self, access_token: str) -> UserEntity:
        """現在のユーザー情報を取得する"""
        try:
            payload = SecurityUtils.decode_token(access_token)
            if not payload or payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="無効なトークンです",
                )

            user_id = payload.get("sub")
            return await self.get_user(str(user_id))

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"認証エラー: {str(e)}"
            )
