from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.studyRecord.study_record_entity import StudyRecordEntity


class StudyRecordRepository(ABC):
    """認証機能のリポジトリインターフェース"""

    @abstractmethod
    async def getAllByUserId(self, userId: UUID) -> StudyRecordEntity:
        """ユーザーに紐づく学習記録を取得する"""
        pass
