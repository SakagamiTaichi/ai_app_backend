from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserEntity(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""

    userId: UUID = Field(..., description="ユーザーID")
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    isActive: bool = Field(..., description="アクティブ状態")
