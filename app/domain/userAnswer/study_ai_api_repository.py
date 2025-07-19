from abc import ABC, abstractmethod
from app.domain.userAnswer.ai_evaluation_value_object import AIEvaluationValueObject


class StudyAiApiRepository(ABC):
    """英語学習関連データのリポジトリインターフェース"""

    @abstractmethod
    async def get_ai_evaluation(
        self, question: str, userAnswer: str
    ) -> AIEvaluationValueObject:
        """AIによって採点された結果を取得する"""
        pass
