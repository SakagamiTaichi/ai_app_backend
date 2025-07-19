from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from app.domain.recall.reacall_card_entity import RecallCardEntity


class RecallCardrepository(ABC):
    """認証機能のリポジトリインターフェース"""

    @abstractmethod
    async def getAllByUserId(self, user_id: str) -> List[RecallCardEntity]:
        """ユーザーに紐づく全ての復習カードを取得する"""
        pass

    @abstractmethod
    async def getByRecallCardIdAndUserId(
        self, recall_card_id: UUID, user_id: UUID
    ) -> RecallCardEntity | None:
        """復習カードIDに紐づく復習カードを取得する"""
        pass

    @abstractmethod
    async def getMostOverdueDeadline(self, user_id: UUID) -> RecallCardEntity | None:
        """期限が最も過ぎている復習カードを取得する"""
        pass

    @abstractmethod
    async def updateAll(self, recall_cards: List[RecallCardEntity]) -> None:
        """復習カードを更新する"""
        pass

    @abstractmethod
    async def createAll(self, recall_cards: List[RecallCardEntity]) -> None:
        """復習カードを作成する"""
        pass
