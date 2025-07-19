import datetime
from pydantic import BaseModel, Field


class LearningHistoryEntity(BaseModel):
    """学習記録を表すエンティティ"""

    userId: str = Field(..., description="ユーザーID")
    date: datetime.date = Field(..., description="学習日")  # 日付のみ
    learningTime: int = Field(
        ..., ge=0, le=60 * 60 * 24, description="1日の学習時間"
    )  # 時間はtimedeltaで表現
