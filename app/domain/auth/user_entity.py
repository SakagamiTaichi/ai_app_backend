from pydantic import BaseModel, EmailStr, Field

class UserResponse(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""
    id: str = Field(..., description="ユーザーID")
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    is_active: bool = Field(..., description="アクティブ状態")