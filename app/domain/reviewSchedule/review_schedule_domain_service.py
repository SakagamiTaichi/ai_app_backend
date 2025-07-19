import datetime
from uuid import UUID
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)


class ReviewScheduleDomainService:
    def __init__(
        self,
        reviewShceduleRepository: ReviewScheduleRepository,
    ):
        self.reviewShceduleRepository = reviewShceduleRepository

    async def get_after_deadline_count(self, user_id: UUID) -> int:
        """復習期限を過ぎた学習記録の数を取得する。"""

        review_schedules = await self.reviewShceduleRepository.getAllByUserId(user_id)
        now = datetime.datetime.now()

        overdue_count = sum(
            1 for schedule in review_schedules if schedule.reviewDeadLine < now
        )

        return overdue_count
