from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from app.core.app_exception import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import SecurityUtils
from app.domain.auth.auth_repository import AuthRepository
from app.domain.auth.login_information_value_object import LoginInformationValueObject
from app.domain.auth.refresh_token_value_object import RefreshTokenValueObject
from app.domain.auth.token_value_object import TokenValueObject
from app.domain.auth.user_entity import UserEntity
from app.domain.auth.password_reset_token_entity import PasswordResetTokenEntity
from app.schema.auth.models import (
    UserModel,
    VerificationCodeModel,
    PasswordResetTokenModel,
)
from app.core.config import settings
import secrets


class AuthPostgresRepository(AuthRepository):
    """PostgreSQLを使用した認証リポジトリの実装"""

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def save_verification_code(self, email: str) -> str:
        try:
            # 既存の未使用コードを無効化
            await self.db.execute(
                VerificationCodeModel.__table__.update()
                .where(
                    and_(
                        VerificationCodeModel.email == email,
                        VerificationCodeModel.is_used == False,
                    )
                )
                .values(is_used=True)
            )

            # 新しい認証コードを生成
            code = SecurityUtils.generate_verification_code()
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES
            )

            # データベースに保存（認証試行回数とロック状態をリセット）
            verification = VerificationCodeModel(
                email=email,
                code=code,
                expires_at=expires_at,
                is_used=False,
                verification_attempts=0,
                is_locked=False,
            )
            self.db.add(verification)
            await self.db.commit()

            return code
        except Exception as e:
            await self.db.rollback()
            raise

    async def _verify_code(self, email: str, code: str) -> bool:
        """認証コードを検証する（試行回数制限付き）"""
        try:
            # 最新の認証コードを取得（有効期限内でis_used=False）
            result = await self.db.execute(
                select(VerificationCodeModel)
                .where(
                    and_(
                        VerificationCodeModel.email == email,
                        VerificationCodeModel.is_used == False,
                        VerificationCodeModel.expires_at > datetime.now(timezone.utc),
                    )
                )
                .order_by(VerificationCodeModel.created_at.desc())
            )
            verification = result.scalar_one_or_none()

            if not verification:
                return False

            # ロックされている場合は認証を拒否
            if verification.is_locked:  # type: ignore
                raise UnauthorizedError(
                    detail="認証試行回数が上限に達したため、この認証コードはロックされています。新しい認証コードを取得してください。"
                )

            # コードが一致するかチェック
            if verification.code != code:  # type: ignore
                # 試行回数を増加
                verification.verification_attempts += 1  # type: ignore

                # 3回以上試行した場合はロック
                if verification.verification_attempts >= 3:  # type: ignore
                    verification.is_locked = True  # type: ignore
                    await self.db.commit()
                    raise UnauthorizedError(
                        detail="認証コードの入力に3回失敗したため、この認証コードはロックされました。新しい認証コードを取得してください。"
                    )

                await self.db.commit()
                remaining_attempts = 3 - verification.verification_attempts  # type: ignore
                raise UnauthorizedError(
                    detail=f"認証コードが正しくありません。残り試行回数: {remaining_attempts}回"
                )

            # 認証成功 - 使用済みにマーク
            verification.is_used = True  # type: ignore
            await self.db.commit()
            return True

        except Exception as e:
            await self.db.rollback()
            raise

    async def signup(self, email: str, password: str, code: str) -> TokenValueObject:
        """新規ユーザーを登録する"""
        try:

            # 認証コードを検証
            is_valid = await self._verify_code(email, code)
            if not is_valid:
                raise UnauthorizedError(
                    detail="認証コードが無効か、有効期限が切れています。"
                )

            # 既存ユーザーのチェック
            # ※User Enumeration Attackにつながるため、認証コード送信時にユーザーチェックを行うのではなく、新規登録時に行う
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )

            existing_user = result.scalar_one_or_none()

            if existing_user:
                raise ConflictError(detail="このメールアドレスは既に使用されています。")

            # パスワードのハッシュ化
            hashed_password = SecurityUtils.get_password_hash(password)

            # 新規ユーザーの作成
            new_user = UserModel(
                email=email, hashed_password=hashed_password, is_active=True
            )

            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            # トークンの生成
            access_token = SecurityUtils.create_access_token({"sub": str(new_user.id)})
            refresh_token = SecurityUtils.create_refresh_token(
                {"sub": str(new_user.id)}
            )

            return TokenValueObject(
                access_token=access_token,
                refresh_token=RefreshTokenValueObject(refresh_token=refresh_token),
                token_type="bearer",
            )

        except Exception as e:
            await self.db.rollback()
            raise

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
                raise UnauthorizedError(
                    detail="メールアドレスまたはパスワードが誤っています。"
                )

            # トークンの生成
            access_token = SecurityUtils.create_access_token({"sub": str(user.id)})
            refresh_token = SecurityUtils.create_refresh_token({"sub": str(user.id)})

            return TokenValueObject(
                access_token=access_token,
                refresh_token=RefreshTokenValueObject(refresh_token=refresh_token),
                token_type="bearer",
            )

        except Exception as e:
            raise

    async def refresh_token(self, refresh_token: str) -> TokenValueObject:
        """リフレッシュトークンを使用して新しいアクセストークンを取得する"""
        try:
            payload = SecurityUtils.decode_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                raise UnauthorizedError(detail="無効なリフレッシュトークンです。")

            user_id = payload.get("sub")

            # 新しいトークンの生成
            access_token = SecurityUtils.create_access_token({"sub": user_id})
            new_refresh_token = SecurityUtils.create_refresh_token({"sub": user_id})

            return TokenValueObject(
                access_token=access_token,
                refresh_token=RefreshTokenValueObject(refresh_token=new_refresh_token),
                token_type="bearer",
            )

        except Exception as e:
            raise

    async def get_user(self, user_id: str) -> UserEntity:
        """ユーザー情報を取得する"""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise NotFoundError(detail="指定されたユーザーは存在しません。")

            return UserEntity(
                id=str(user.id), email=str(user.email), is_active=bool(user.is_active)
            )

        except Exception as e:
            raise

    async def get_current_user(self, access_token: str) -> UserEntity:
        """現在のユーザー情報を取得する"""
        try:
            payload = SecurityUtils.decode_token(access_token)
            if not payload or payload.get("type") != "access":
                raise UnauthorizedError(detail="無効なアクセストークンです。")

            user_id = payload.get("sub")
            return await self.get_user(str(user_id))

        except Exception as e:
            raise

    async def create_password_reset_token(self, email: str) -> str:
        """パスワードリセットトークンを生成して保存する"""
        try:
            # ユーザーが存在するかチェック
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalar_one_or_none()
            if not user:
                # セキュリティ上、メールアドレスが存在しない場合でもエラーにしない
                # ただし、実際にはトークンを作成しない
                return ""

            # 既存の未使用トークンを無効化
            await self.db.execute(
                PasswordResetTokenModel.__table__.update()
                .where(
                    and_(
                        PasswordResetTokenModel.email == email,
                        PasswordResetTokenModel.is_used == False,
                    )
                )
                .values(is_used=True)
            )

            # 新しいパスワードリセットトークンを生成
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES  # 同じ有効期限を使用
            )

            # データベースに保存
            reset_token = PasswordResetTokenModel(
                email=email, token=token, expires_at=expires_at, is_used=False
            )
            self.db.add(reset_token)
            await self.db.commit()

            return token

        except Exception as e:
            await self.db.rollback()
            raise

    async def get_password_reset_token(self, token: str) -> PasswordResetTokenEntity:
        """パスワードリセットトークンを取得する"""
        try:
            result = await self.db.execute(
                select(PasswordResetTokenModel).where(
                    and_(
                        PasswordResetTokenModel.token == token,
                        PasswordResetTokenModel.is_used == False,
                        PasswordResetTokenModel.expires_at > datetime.now(timezone.utc),
                    )
                )
            )
            reset_token = result.scalar_one_or_none()

            if not reset_token:
                raise NotFoundError(detail="無効または期限切れのリセットトークンです。")

            return PasswordResetTokenEntity(
                id=str(reset_token.id),
                email=reset_token.email,  # type: ignore
                token=reset_token.token,  # type: ignore
                is_used=reset_token.is_used,  # type: ignore
                expires_at=reset_token.expires_at,  # type: ignore
                created_at=reset_token.created_at,  # type: ignore
                used_at=reset_token.used_at,  # type: ignore
            )

        except Exception as e:
            raise

    async def reset_password(self, token: str, new_password: str) -> bool:
        """パスワードをリセットする"""
        try:
            # トークンの検証
            reset_token_entity = await self.get_password_reset_token(token)

            # ユーザーを取得
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == reset_token_entity.email)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise NotFoundError(detail="ユーザーが見つかりません。")

            # パスワードを更新
            user.hashed_password = SecurityUtils.get_password_hash(new_password)  # type: ignore
            user.updated_at = datetime.now(timezone.utc)  # type: ignore

            # トークンを使用済みにマーク
            result = await self.db.execute(
                select(PasswordResetTokenModel).where(
                    PasswordResetTokenModel.token == token
                )
            )
            db_token = result.scalar_one()
            db_token.is_used = True  # type: ignore
            db_token.used_at = datetime.now(timezone.utc)  # type: ignore

            await self.db.commit()
            return True

        except Exception as e:
            await self.db.rollback()
            raise
