from pydantic import BaseModel, Field

from app.domain.auth.refresh_token_value_object import RefreshTokenValueObject


class TokenValueObject(BaseModel):
    """認証トークン用のスキーマ"""

    accessToken: str = Field(
        ...,
        description="アクセストークン",
        min_length=22,
        max_length=859,
        pattern=r"^[a-zA-Z0-9_\-\.]+$",
    )
    refreshToken: RefreshTokenValueObject = Field(
        ...,
        description="リフレッシュトークン",
    )
    tokenType: str = Field("bearer", description="トークンタイプ", pattern=r"^bearer$")
