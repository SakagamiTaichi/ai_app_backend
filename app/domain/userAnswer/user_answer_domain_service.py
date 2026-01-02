from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Enum
from app.core.app_exception import NotFoundError
from app.domain.quiz.quize_entity import QuizEntity
from app.domain.quiz.quize_repostiroy import QuizRepository
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)
from app.domain.userAnswer.user_answer_repository import UserAnswerRepository

import random


class QuestionType(str, Enum):
    NEW = "new"
    REVIEW = "review"
    MIXED = "mixed"


class UserAnswerDomainService:
    def __init__(
        self,
        quizRepository: QuizRepository,
        userAnswerRepository: UserAnswerRepository,
        reviewScheduleRepository: ReviewScheduleRepository,
    ):
        self.quizRepository = quizRepository
        self.userAnswerRepository = userAnswerRepository
        self.reviewScheduleRepository = reviewScheduleRepository

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

    async def get_next_quiz(
        self, user_id: UUID, quizTypeId: Optional[UUID], questionType: Optional[str]
    ) -> QuizEntity:
        """ユーザーの次のクイズを取得する。"""

        if not quizTypeId is None:
            quizzes = await self.quizRepository.getAllByQuizTypeId(quizTypeId)
        else:
            quizzes = await self.quizRepository.getAll()

        not_answered_quizzes = []
        if questionType == QuestionType.NEW or questionType == QuestionType.MIXED:
            answered_quiz_ids = {
                answer.quizId
                for answer in await self.userAnswerRepository.getAllByUserId(user_id)
            }

            not_answered_quizzes = [
                quiz for quiz in quizzes if quiz.quizId not in answered_quiz_ids
            ]

        deadline_quizzes = []
        if questionType == QuestionType.REVIEW or questionType == QuestionType.MIXED:
            reviewSchedules = await self.reviewScheduleRepository.getAllByUserId(
                user_id
            )
            deadline_quizzes = [
                quiz
                for quiz in quizzes
                if any(
                    schedule.quizId == quiz.quizId
                    and schedule.reviewDeadLine < datetime.now()
                    for schedule in reviewSchedules
                )
            ]

            # deadline_quizzes.sort(
            #     key=lambda quiz: min(
            #         schedule.reviewDeadLine
            #         for schedule in reviewSchedules
            #         if schedule.quizId == quiz.quizId
            #         and schedule.reviewDeadLine < datetime.now()
            #     )
            # )
        match questionType:
            case QuestionType.REVIEW:
                # 復習クイズの中から一つを返す
                if deadline_quizzes:
                    random.shuffle(deadline_quizzes)
                    return deadline_quizzes[0]
                else:
                    raise NotFoundError("挑戦可能なクイズが存在しません。")
                # ただし存在しない場合はエラーを返す

            case QuestionType.NEW:
                # 新規クイズの中から一つを返す
                if not_answered_quizzes:
                    # シャッフルする
                    random.shuffle(not_answered_quizzes)
                    return not_answered_quizzes[0]
                else:
                    raise NotFoundError("挑戦可能なクイズが存在しません。")
                # ただし存在しない場合はエラーを返す

            case QuestionType.MIXED:
                # 復習クイズと新規クイズの中から一つを返
                # 復習クイズと新規クイズをミックスする。ただし、数を同数にする
                all_quizzes = not_answered_quizzes + deadline_quizzes

                if all_quizzes:
                    # シャッフルしてランダムに一つを返す
                    random.shuffle(all_quizzes)
                    return all_quizzes[0]
                else:
                    raise NotFoundError("挑戦可能なクイズが存在しません。")

            case _:
                # クイズの種類が指定されていない場合はエラーを返す
                raise NotFoundError("クイズの種類が指定されていません。")
