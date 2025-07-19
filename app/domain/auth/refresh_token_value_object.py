from pydantic import BaseModel, Field


class RefreshTokenValueObject(BaseModel):
    """認証トークン用のスキーマ"""

    refreshToken: str = Field(
        ...,
        description="リフレッシュトークン",
        min_length=22,
        max_length=859,
        pattern=r"^[a-zA-Z0-9_\-\.]+$",
    )
