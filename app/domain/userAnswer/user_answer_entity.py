import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.domain.userAnswer.ai_evaluation_value_object import AIEvaluationValueObject


class UserAnswerEntity(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""

    userAnswerId: UUID = Field(..., description="ユーザー回答ID")
    userId: UUID = Field(..., description="ユーザーID")
    quizId: UUID = Field(..., description="クイズID")
    answer: str = Field(..., description="回答")
    aiEvaluation: AIEvaluationValueObject = Field(..., description="AI評価")
    answeredAt: datetime.datetime = Field(..., description="回答日時")
