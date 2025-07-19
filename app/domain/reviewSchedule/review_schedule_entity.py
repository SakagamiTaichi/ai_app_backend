import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ReviewScheduleEntity(BaseModel):
    """復習スケジュールエンティティ"""

    reviewScheduleId: UUID = Field(..., description="復習スケジュールID")
    userId: UUID = Field(..., description="ユーザーID")
    quizId: UUID = Field(..., description="クイズID")
    reviewDeadLine: datetime.date = Field(..., description="復習期限")
