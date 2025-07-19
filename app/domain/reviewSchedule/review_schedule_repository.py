from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from app.domain.reviewSchedule.review_schedule_entity import ReviewScheduleEntity


class ReviewScheduleRepository(ABC):
    """復習スケジュールのリポジトリインターフェース"""

    @abstractmethod
    async def getAllByUserId(self, userId: UUID) -> List[ReviewScheduleEntity]:
        """ユーザーに紐づく復習スケジュールを取得する"""
        pass
