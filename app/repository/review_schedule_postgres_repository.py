from typing import List, Optional
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

    async def get_schedule(
        self, userId: UUID, quizId: UUID
    ) -> Optional[ReviewScheduleEntity]:
        """特定のクイズに対するユーザーの復習スケジュールを取得する"""
        try:
            # 特定のクイズに対する復習スケジュールを取得
            result = await self.db.execute(
                select(ReviewSchedules).where(
                    ReviewSchedules.user_id == userId,
                    ReviewSchedules.quiz_id == quizId,
                )
            )

            schedule = result.scalar_one_or_none()

            if schedule is None:
                return None

            # SQLAlchemyモデルをエンティティに変換
            return ReviewScheduleEntity(
                reviewScheduleId=schedule.review_schedule_id,  # type: ignore
                userId=schedule.user_id,  # type: ignore
                quizId=schedule.quiz_id,  # type: ignore
                reviewDeadLine=schedule.review_deadline.date(),  # type: ignore
            )

        except Exception:
            await self.db.rollback()
            raise

    async def create(
        self, reviewSchedule: ReviewScheduleEntity
    ) -> ReviewScheduleEntity:
        """新しい復習スケジュールを作成する"""
        try:
            # SQLAlchemyモデルをエンティティに変換
            new_schedule = ReviewSchedules(
                review_schedule_id=reviewSchedule.reviewScheduleId,
                user_id=reviewSchedule.userId,
                quiz_id=reviewSchedule.quizId,
                review_deadline=reviewSchedule.reviewDeadLine,
            )

            self.db.add(new_schedule)
            await self.db.commit()
            await self.db.refresh(new_schedule)

            return ReviewScheduleEntity(
                reviewScheduleId=new_schedule.review_schedule_id,  # type: ignore
                userId=new_schedule.user_id,  # type: ignore
                quizId=new_schedule.quiz_id,  # type: ignore
                reviewDeadLine=new_schedule.review_deadline.date(),  # type: ignore
            )

        except Exception:
            await self.db.rollback()
            raise

    async def update(
        self, reviewSchedule: ReviewScheduleEntity
    ) -> ReviewScheduleEntity:
        """既存の復習スケジュールを更新する"""
        try:
            # SQLAlchemyモデルを取得
            result = await self.db.execute(
                select(ReviewSchedules).where(
                    ReviewSchedules.review_schedule_id
                    == reviewSchedule.reviewScheduleId
                )
            )

            schedule = result.scalar_one_or_none()

            if schedule is None:
                raise ValueError("復習スケジュールが見つかりません")

            # 復習期限を更新
            schedule.review_deadline = reviewSchedule.reviewDeadLine  # type: ignore

            await self.db.commit()
            await self.db.refresh(schedule)

            return ReviewScheduleEntity(
                reviewScheduleId=schedule.review_schedule_id,  # type: ignore
                userId=schedule.user_id,  # type: ignore
                quizId=schedule.quiz_id,  # type: ignore
                reviewDeadLine=schedule.review_deadline.date(),  # type: ignore
            )

        except Exception:
            await self.db.rollback()
            raise
