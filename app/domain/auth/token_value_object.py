from pydantic import BaseModel, Field

from app.domain.auth.refresh_token_value_object import RefreshTokenValueObject

class TokenValueObject(BaseModel):
    """認証トークン用のスキーマ"""
    access_token: str = Field(
        ..., 
        description="アクセストークン",
        min_length=22,
        max_length=859,
        pattern=r"^[a-zA-Z0-9_\-\.]+$"
    )
    refresh_token: RefreshTokenValueObject = Field(
        ..., 
        description="リフレッシュトークン", 
    )
    token_type: str = Field(
        "bearer", 
        description="トークンタイプ",
        pattern=r"^bearer$"
    )