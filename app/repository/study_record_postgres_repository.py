from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.domain.studyRecord.study_record_entity import StudyRecordEntity
from app.domain.studyRecord.study_record_repository import StudyRecordRepository
from app.domain.studyRecord.dailyt_study_record_value_object import (
    DailyStudyRecordValueObject,
)
from app.schema.models import StudyRecords


class StudyRecordPostgresRepository(StudyRecordRepository):
    """PostgreSQL用の学習記録リポジトリ実装"""

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def getAllByUserId(self, userId: UUID) -> StudyRecordEntity:
        """ユーザーに紐づく全ての学習記録を取得する"""
        try:
            # ユーザーの学習記録を取得（関連する日次記録も含める）
            result = await self.db.execute(
                select(StudyRecords)
                .options(selectinload(StudyRecords.daily_study_records))
                .where(StudyRecords.user_id == userId)
            )

            study_record = result.scalar_one_or_none()

            if study_record is None:
                # 学習記録が存在しない場合は新規作成
                new_study_record = StudyRecords(
                    user_id=userId,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                self.db.add(new_study_record)
                await self.db.commit()
                await self.db.refresh(new_study_record)

                return StudyRecordEntity(
                    studyRcordId=new_study_record.study_record_id,  # type: ignore
                    userId=userId,
                    dailyStudyRecords=[],
                )

            # 日次学習記録をDailyStudyRecordValueObjectに変換
            daily_records = [
                DailyStudyRecordValueObject(
                    date=daily_record.date.date(),  # type: ignore
                    studyTime=daily_record.study_time,  # type: ignore
                )
                for daily_record in study_record.daily_study_records
            ]

            return StudyRecordEntity(
                studyRcordId=study_record.study_record_id,  # type: ignore
                userId=study_record.user_id,  # type: ignore
                dailyStudyRecords=daily_records,
            )

        except Exception as e:
            await self.db.rollback()
            raise
