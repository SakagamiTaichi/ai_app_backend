from enum import IntEnum, auto
from uuid import UUID
from pydantic import BaseModel, Field


class DifficultyEnum(IntEnum):
    """難易度の列挙型"""

    やさしい = auto()
    ふつう = auto()
    難しい = auto()


class QuizEntity(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""

    quizId: UUID = Field(..., description="クイズ種類ID")
    question: str = Field(..., min_length=1, max_length=300, description="内容")
    modelAnswer: str = Field(..., min_length=1, max_length=300, description="模範解答")
    quizTypeId: UUID = Field(..., description="種類ID")
    difficulty: DifficultyEnum = Field(..., description="難易度")
