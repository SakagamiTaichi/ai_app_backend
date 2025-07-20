from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.reviewSchedule.review_schedule_entity import ReviewScheduleEntity


class ReviewScheduleRepository(ABC):
    """復習スケジュールのリポジトリインターフェース"""

    @abstractmethod
    async def getAllByUserId(self, userId: UUID) -> List[ReviewScheduleEntity]:
        """ユーザーに紐づく復習スケジュールを取得する"""
        pass

    @abstractmethod
    async def get_schedule(
        self, userId: UUID, quizId: UUID
    ) -> Optional[ReviewScheduleEntity]:
        """特定のクイズに対するユーザーの復習スケジュールを取得する"""
        pass

    @abstractmethod
    async def create(
        self, reviewSchedule: ReviewScheduleEntity
    ) -> ReviewScheduleEntity:
        """新しい復習スケジュールを作成する"""
        pass

    @abstractmethod
    async def update(
        self, reviewSchedule: ReviewScheduleEntity
    ) -> ReviewScheduleEntity:
        """既存の復習スケジュールを更新する"""
        pass
