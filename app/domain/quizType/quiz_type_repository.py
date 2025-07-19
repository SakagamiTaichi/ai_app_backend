from abc import ABC, abstractmethod
from typing import List
from app.domain.quizType.quiz_type_entity import QuizTypeEntity


class QuizTypeRepository(ABC):
    """クイズの種類のリポジトリインターフェース"""

    @abstractmethod
    async def getAll(self) -> List[QuizTypeEntity]:
        """全てのクイズの種類を取得する"""
        pass
