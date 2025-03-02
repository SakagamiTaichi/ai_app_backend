from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """ユーザー基本情報のベースモデル"""
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    username: str = Field(..., description="ユーザー名")


class UserCreate(UserBase):
    """ユーザー作成リクエストモデル"""
    password: str = Field(..., description="ユーザーのパスワード", min_length=8)


class UserResponse(UserBase):
    """ユーザー情報レスポンスモデル"""
    id: str = Field(..., description="ユーザーのID")
    created_at: datetime = Field(..., description="アカウント作成日時")
    updated_at: datetime = Field(..., description="アカウント更新日時")


class Token(BaseModel):
    """認証トークンレスポンスモデル"""
    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field("bearer", description="トークンタイプ")
    user: UserResponse = Field(..., description="ユーザー情報")


class TokenData(BaseModel):
    """トークンデータモデル（内部処理用）"""
    user_id: str = Field(..., description="ユーザーID")
    exp: Optional[datetime] = Field(None, description="有効期限")


class LoginRequest(BaseModel):
    """ログインリクエストモデル"""
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    password: str = Field(..., description="ユーザーのパスワード")