from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.entities.test_result import TestResult
from app.features.practice.model.practice import Conversation, Message

class PracticeRepository(ABC):
    """英語学習関連データのリポジトリインターフェース"""
    
    @abstractmethod
    async def get_conversation_sets(self, user_id: str) -> List[Conversation]:
        """特定ユーザーの会話セットの一覧を取得する"""
        pass
    
    @abstractmethod
    async def get_messages(self, conversation_id: UUID, user_id: str) -> List[Message]:
        """特定の会話セットに属するメッセージを取得する（アクセス権の確認あり）"""
        pass
    
    @abstractmethod
    async def create_message(self, message: Message) -> Message:
        """メッセージを作成する"""
        pass
    
    @abstractmethod
    async def create_conversation_set(self, conversation_set: Conversation) -> Conversation:
        """会話セットを作成する"""
        pass

    @abstractmethod
    async def save_test_result(self, test_result: TestResult) -> TestResult:
        """テスト結果をデータベースに保存する"""
        pass
    
    @abstractmethod
    async def get_latest_test_result(self, conversation_id: UUID) -> Optional[TestResult]:
        """指定された会話の最新のテスト結果を取得する"""
        pass
    