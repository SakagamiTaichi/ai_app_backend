from pydantic import BaseModel, Field

class TokenValueObject(BaseModel):
    """認証トークン用のスキーマ"""
    access_token: str = Field(
        ..., 
        description="アクセストークン",
        min_length=22,
        max_length=859,
        pattern=r"^[a-zA-Z0-9_\-\.]+$"
    )
    refresh_token: str = Field(
        ..., 
        description="リフレッシュトークン", 
        min_length=22,
        max_length=859,
        pattern=r"^[a-zA-Z0-9_\-\.]+$"
    )
    token_type: str = Field(
        "bearer", 
        description="トークンタイプ",
        pattern=r"^bearer$"
    )