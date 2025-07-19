from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.reviewSchedule.review_schedule_entity import ReviewScheduleEntity
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)
from app.schema.models import ReviewSchedules


class ReviewSchedulePostgresRepository(ReviewScheduleRepository):
    """PostgreSQL用の学習記録リポジトリ実装"""

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def getAllByUserId(self, userId: UUID) -> List[ReviewScheduleEntity]:
        """ユーザーに紐づく全ての復習スケジュールを取得する"""
        try:
            # ユーザーに紐づく復習スケジュールを取得
            result = await self.db.execute(
                select(ReviewSchedules).where(ReviewSchedules.user_id == userId)
            )

            review_schedules = result.scalars().all()

            # SQLAlchemyモデルをエンティティに変換
            return [
                ReviewScheduleEntity(
                    reviewScheduleId=schedule.review_schedule_id,  # type: ignore
                    userId=schedule.user_id,  # type: ignore
                    quizId=schedule.quiz_id,  # type: ignore
                    reviewDeadLine=schedule.review_deadline.date(),  # type: ignore
                )
                for schedule in review_schedules
            ]

        except Exception:
            await self.db.rollback()
            raise
