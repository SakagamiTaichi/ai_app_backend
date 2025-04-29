from abc import ABC, abstractmethod
from app.domain.practice.geneerated_conversation_value_object import GeneratedConversationValueObject


class PracticeApiRepository(ABC):
    """英語学習関連データのリポジトリインターフェース"""
    
    @abstractmethod
    async def get_generated_conversation(self, user_phrase: str) -> GeneratedConversationValueObject:
        """AIによって生成された会話を取得する"""
        pass