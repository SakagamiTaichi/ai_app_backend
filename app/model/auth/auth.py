from pydantic import BaseModel, EmailStr, Field


class SignUpRequestModel(BaseModel):
    """ユーザー登録用のスキーマ"""

    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    password: str = Field(..., min_length=8, description="パスワード (8文字以上)")
    code: str = Field(..., description="認証コード")


class UserLoginRequest(BaseModel):
    """ユーザーログイン用のスキーマ"""

    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    password: str = Field(..., description="パスワード")


class TokenResponse(BaseModel):
    """認証トークン用のスキーマ"""

    access_token: str = Field(..., description="アクセストークン")
    refresh_token: str = Field(..., description="リフレッシュトークン")
    token_type: str = Field("bearer", description="トークンタイプ")


class UserResponse(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""

    id: str = Field(..., description="ユーザーID")
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    is_active: bool = Field(..., description="アクティブ状態")


class VerificationCodeResponse(BaseModel):
    """認証コード送信レスポンス用のスキーマ"""

    email: EmailStr = Field(..., description="メールアドレス")


class VerificationCodeRequest(BaseModel):
    """認証コード送信リクエスト用のスキーマ"""

    email: EmailStr = Field(..., description="ユーザーのメールアドレス")


class PasswordResetRequestModel(BaseModel):
    """パスワードリセット要求用のスキーマ"""

    email: EmailStr = Field(..., description="ユーザーのメールアドレス")


class PasswordResetModel(BaseModel):
    """パスワードリセット実行用のスキーマ"""

    token: str = Field(..., description="パスワードリセットトークン")
    new_password: str = Field(..., min_length=8, description="新しいパスワード (8文字以上)")


class PasswordResetResponse(BaseModel):
    """パスワードリセット成功レスポンス用のスキーマ"""

    message: str = Field(..., description="成功メッセージ")
