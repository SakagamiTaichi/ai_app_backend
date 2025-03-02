from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """ユーザー登録用のスキーマ"""
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    password: str = Field(..., min_length=8, description="パスワード (8文字以上)")
    
class UserLogin(BaseModel):
    """ユーザーログイン用のスキーマ"""
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    password: str = Field(..., description="パスワード")

class Token(BaseModel):
    """認証トークン用のスキーマ"""
    access_token: str = Field(..., description="アクセストークン")
    refresh_token: str = Field(..., description="リフレッシュトークン")
    token_type: str = Field("bearer", description="トークンタイプ")

class TokenPayload(BaseModel):
    """トークンのペイロード用のスキーマ"""
    sub: str = Field(..., description="サブジェクト (ユーザーID)")
    exp: int = Field(..., description="有効期限 (UNIX時間)")

class UserResponse(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""
    id: str = Field(..., description="ユーザーID")
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    is_active: bool = Field(..., description="アクティブ状態")