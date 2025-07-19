import datetime
from pydantic import BaseModel, Field


class DailyStudyRecordValueObject(BaseModel):
    """日次学習記録の値オブジェクト"""

    date: datetime.date = Field(..., description="学習記録ID")
    studyTime: int = Field(
        ..., ge=0, le=60 * 60 * 24, description="1日の学習時間"
    )  # 時間はtimedeltaで表現
