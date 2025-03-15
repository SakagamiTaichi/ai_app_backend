from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.schemas.english_chat import Conversation, Message

class EnglishRepository(ABC):
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