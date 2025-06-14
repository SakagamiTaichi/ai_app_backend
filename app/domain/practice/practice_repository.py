from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.practice.conversation_entity import ConversationEntity
from app.domain.practice.test_result_entity import TestResultEntity
from app.endpoint.practice.practice_model import MessageResponse


class PracticeRepository(ABC):
    """英語学習関連データのリポジトリインターフェース"""

    @abstractmethod
    async def fetchAll(self, user_id: str) -> List[ConversationEntity]:
        """特定ユーザーの会話セットの一覧を取得する"""
        pass

    @abstractmethod
    async def reorder_conversations(
        self, user_id: str, conversation_ids: List[UUID]
    ) -> None:
        """会話セットの順序を変更する"""
        pass

    @abstractmethod
    async def fetch(self, conversation_id: UUID, user_id: str) -> List[MessageResponse]:
        """特定の会話セットに属するメッセージを取得する（アクセス権の確認あり）"""
        pass

    @abstractmethod
    async def create_message(self, message: MessageResponse) -> MessageResponse:
        """メッセージを作成する"""
        pass

    @abstractmethod
    async def create(self, conversation_set: ConversationEntity) -> None:
        """会話セットを作成する"""
        pass

    @abstractmethod
    async def save_test_result(self, test_result: TestResultEntity) -> TestResultEntity:
        """テスト結果をデータベースに保存する"""
        pass

    @abstractmethod
    async def get_latest_test_result(
        self, conversation_id: UUID
    ) -> Optional[TestResultEntity]:
        """指定された会話の最新のテスト結果を取得する"""
        pass
