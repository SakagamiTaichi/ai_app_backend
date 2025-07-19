from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from app.domain.userAnswer.user_answer_entity import UserAnswerEntity


class UserAnswerRepository(ABC):
    """ユーザーのクイズ回答のリポジトリインターフェース"""

    @abstractmethod
    async def getById(self, userAnswerId: UUID) -> UserAnswerEntity:
        """ユーザーの回答をIDで取得する"""
        pass

    @abstractmethod
    async def getAllByUserId(self, userId: UUID) -> List[UserAnswerEntity]:
        """ユーザーに紐づく全てのクイズ回答を取得する"""
        pass

    @abstractmethod
    async def getAllByQuizIdUserId(
        self, userId: UUID, quizId: UUID
    ) -> List[UserAnswerEntity]:
        """ユーザーとクイズに紐づく全てのクイズ回答を取得する"""
        pass

    @abstractmethod
    async def create(self, userAnswerEntity: UserAnswerEntity) -> None:
        """ユーザーの回答を新規作成する"""
        pass
