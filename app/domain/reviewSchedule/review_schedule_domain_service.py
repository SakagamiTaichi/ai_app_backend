import datetime
from typing import List
from uuid import UUID
from app.domain.reviewSchedule.review_schedule_entity import ReviewScheduleEntity
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)


class ReviewScheduleDomainService:
    def __init__(
        self,
        reviewShceduleRepository: ReviewScheduleRepository,
    ):
        self.reviewShceduleRepository = reviewShceduleRepository

    async def get_review_schedule(self, user_id: UUID) -> List[ReviewScheduleEntity]:
        """ユーザーの復習スケジュールを取得する。"""
        return await self.reviewShceduleRepository.getAllByUserId(user_id)

    async def get_after_deadline_count(self, user_id: UUID) -> tuple[int, int]:
        """復習期限を過ぎた学習記録の数を取得する。"""

        review_schedules = await self.reviewShceduleRepository.getAllByUserId(user_id)
        now = datetime.datetime.now()

        overdue_count = sum(
            1 for schedule in review_schedules if schedule.reviewDeadLine < now
        )

        underdue_count = sum(
            1 for schedule in review_schedules if schedule.reviewDeadLine >= now
        )

        return overdue_count, underdue_count
