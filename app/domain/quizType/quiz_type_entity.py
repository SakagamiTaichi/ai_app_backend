from uuid import UUID
from pydantic import BaseModel, Field


class QuizTypeEntity(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""

    quizTypeId: UUID = Field(..., description="クイズ種類ID")
    name: str = Field(..., min_length=1, max_length=30, description="名前")
    description: str = Field(..., min_length=1, max_length=300, description="説明")
