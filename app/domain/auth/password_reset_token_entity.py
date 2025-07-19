from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class PasswordResetTokenEntity(BaseModel):
    """パスワードリセットトークンエンティティ"""

    id: str = Field(..., description="トークンID")
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    token: str = Field(..., description="リセットトークン")
    isUsed: bool = Field(default=False, description="使用済みフラグ")
    expiresAt: datetime = Field(..., description="有効期限")
    createdAt: datetime = Field(..., description="作成日時")
    usedAt: Optional[datetime] = Field(None, description="使用日時")
