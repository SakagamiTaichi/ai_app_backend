from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class PasswordResetTokenEntity(BaseModel):
    """パスワードリセットトークンエンティティ"""
    
    id: str = Field(..., description="トークンID")
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    token: str = Field(..., description="リセットトークン")
    is_used: bool = Field(default=False, description="使用済みフラグ")
    expires_at: datetime = Field(..., description="有効期限")
    created_at: datetime = Field(..., description="作成日時")
    used_at: Optional[datetime] = Field(None, description="使用日時")