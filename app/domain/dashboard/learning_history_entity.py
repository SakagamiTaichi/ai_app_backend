import datetime
from pydantic import BaseModel, Field


class LearningHistoryEntity(BaseModel):
    """学習記録を表すエンティティ"""

    user_id: str = Field(..., description="ユーザーID")
    date: datetime.date = Field(..., description="学習日")  # 日付のみ
    learning_time: int = Field(
        ..., ge=0, le=60 * 60 * 24, description="1日の学習時間"
    )  # 時間はtimedeltaで表現
