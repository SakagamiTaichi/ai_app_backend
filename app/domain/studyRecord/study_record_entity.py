from typing import List
from uuid import UUID
from pydantic import BaseModel, Field

from app.domain.studyRecord.dailyt_study_record_value_object import (
    DailyStudyRecordValueObject,
)


class StudyRecordEntity(BaseModel):
    """学習記録エンティティ"""

    studyRcordId: UUID = Field(..., description="学習記録ID")
    userId: UUID = Field(..., description="ユーザーID")
    dailyStudyRecords: List[DailyStudyRecordValueObject] = Field(
        ..., description="日次学習記録一覧"
    )

    def getContinuousLearningDays(self) -> int:
        """連続学習日数を取得する"""
        if not self.dailyStudyRecords:
            return 0

        # 日付でソートして最新のものから順に確認
        sorted_records = sorted(
            self.dailyStudyRecords, key=lambda x: x.date, reverse=True
        )
        continuous_days = 1
        last_date = sorted_records[0].date

        for record in sorted_records[1:]:
            if (last_date - record.date).days == 1:
                continuous_days += 1
                last_date = record.date
            else:
                break

        return continuous_days
