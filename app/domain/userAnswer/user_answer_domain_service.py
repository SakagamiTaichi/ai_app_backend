from typing import List, Optional
from uuid import UUID
from app.domain.quiz.quize_entity import QuizEntity
from app.domain.quiz.quize_repostiroy import QuizRepository
from app.domain.userAnswer.user_answer_repository import UserAnswerRepository


class UserAnswerDomainService:
    def __init__(
        self,
        quizRepository: QuizRepository,
        userAnswerRepository: UserAnswerRepository,
    ):
        self.quizRepository = quizRepository
        self.userAnswerRepository = userAnswerRepository

    async def get_average_score(self, user_id: UUID) -> int:
        """ユーザーの平均スコアを取得する。"""

        userAnswers = await self.userAnswerRepository.getAllByUserId(user_id)
        if not userAnswers:
            return 0

        total_score = sum(answer.aiEvaluation.score for answer in userAnswers)
        average_score = total_score // len(userAnswers)

        return average_score

    async def get_not_answered_quiz_count(self, user_id: UUID) -> int:
        """ユーザーが未回答のクイズ数を取得する。"""

        quizzes = await self.quizRepository.getAll()
        answered_quiz_ids = {
            answer.quizId
            for answer in await self.userAnswerRepository.getAllByUserId(user_id)
        }

        not_answered_count = sum(
            1 for quiz in quizzes if quiz.quizId not in answered_quiz_ids
        )

        return not_answered_count

    async def get_not_answered_quizzes(
        self, user_id: UUID, quizTypeId: Optional[UUID]
    ) -> List[QuizEntity]:
        """ユーザーが未回答のクイズを取得する。"""

        quizzes = await self.quizRepository.getAll()
        answered_quiz_ids = {
            answer.quizId
            for answer in await self.userAnswerRepository.getAllByUserId(user_id)
        }

        not_answered_quizzes = [
            quiz
            for quiz in quizzes
            if quiz.quizId not in answered_quiz_ids
            and (quiz.quizTypeId == quizTypeId or quizTypeId is None)
        ]

        return not_answered_quizzes
