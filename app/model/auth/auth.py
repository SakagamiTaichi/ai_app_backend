from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    """ユーザー登録用のスキーマ"""

    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    password: str = Field(..., min_length=8, description="パスワード (8文字以上)")


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
