from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from app.domain.quiz.quize_entity import QuizEntity


class QuizRepository(ABC):
    """クイズのリポジトリインターフェース"""

    @abstractmethod
    async def getById(self, quizId: UUID) -> QuizEntity:
        """指定されたIDのクイズを取得する"""
        pass

    @abstractmethod
    async def getAll(self) -> List[QuizEntity]:
        """指定されたIDのクイズを除いた全てのクイズを取得する"""
        pass
