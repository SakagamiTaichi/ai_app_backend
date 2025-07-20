import datetime
from typing import Optional
from uuid import UUID, uuid4
from app.domain.quiz.quize_repostiroy import QuizRepository

from app.domain.quizType.quiz_type_repository import QuizTypeRepository
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)
from app.domain.userAnswer.ai_evaluation_value_object import AIEvaluationValueObject
from app.domain.userAnswer.study_ai_api_repository import StudyAiApiRepository
from app.domain.userAnswer.user_answer_domain_service import UserAnswerDomainService
from app.domain.userAnswer.user_answer_entity import UserAnswerEntity
from app.domain.userAnswer.user_answer_repository import UserAnswerRepository
from app.endpoint.study.study_model import (
    QuizAnswerRequest,
    QuizAnswerResponse,
    QuizResponse,
    QuizStudyRecordResponse,
    QuizStudyRecordsResponse,
    QuizTypeResponse,
    QuizTypesResponse,
    QuizResponse,
    StudyRecordsResponse,
    UserAnswerResponse,
)


class StudyService:
    def __init__(
        self,
        quizRepository: QuizRepository,
        userAnswerRepository: UserAnswerRepository,
        quiZTypeRepository: QuizTypeRepository,
        reviewScheduleRepository: ReviewScheduleRepository,
        aiAPIRepository: StudyAiApiRepository,
    ):
        self.quizRepository = quizRepository
        self.userAnswerRepository = userAnswerRepository
        self.quiZTypeRepository = quiZTypeRepository
        self.reviewScheduleRepository = reviewScheduleRepository
        self.aiAPIRepository = aiAPIRepository

    async def get_quiz_type(self) -> QuizTypesResponse:
        """クイズの種類選択画面の情報を取得する。"""
        quizTypes = await self.quiZTypeRepository.getAll()

        return QuizTypesResponse(
            quiz_types=[
                QuizTypeResponse(
                    id=quizType.quizTypeId,
                    name=quizType.name,
                    description=quizType.description,
                )
                for quizType in quizTypes
            ]
        )

    async def get_quizzes(
        self, user_id: UUID, quizTypeId: Optional[UUID], questionType: Optional[str]
    ) -> QuizResponse:
        """クイズの一覧を取得する。"""
        quizzes = await self.quizRepository.getAll()

        userAnswerDomainService = UserAnswerDomainService(
            quizRepository=self.quizRepository,
            userAnswerRepository=self.userAnswerRepository,
            reviewScheduleRepository=self.reviewScheduleRepository,
        )

        # ユーザーが未回答のクイズ一覧を取得する
        not_answered_quiz = await userAnswerDomainService.get_next_quiz(
            user_id, quizTypeId, questionType
        )

        # 5つに絞る
        # not_answered_quiz: QuizEntity = not_answered_quizzes[0]

        # クイズの種類一覧を取得する
        quiz_types = await self.quiZTypeRepository.getAll()

        return QuizResponse(
            id=not_answered_quiz.quizId,
            content=not_answered_quiz.question,
            type=next(
                (
                    quiz_type.name
                    for quiz_type in quiz_types
                    if quiz_type.quizTypeId == not_answered_quiz.quizTypeId
                ),
                "",
            ),
            difficulty=not_answered_quiz.difficulty.name,
        )

    async def get_study_records(self, user_id: UUID) -> QuizStudyRecordsResponse:
        """クイズの学習履歴をまとめて取得する。"""
        quizzes = await self.quizRepository.getAll()
        userAnswers = await self.userAnswerRepository.getAllByUserId(user_id)
        reviewSchedules = await self.reviewScheduleRepository.getAllByUserId(user_id)
        quizeTypes = await self.quiZTypeRepository.getAll()

        return QuizStudyRecordsResponse(
            quiz_types=QuizTypesResponse(
                quiz_types=[
                    QuizTypeResponse(
                        id=quizType.quizTypeId,
                        name=quizType.name,
                        description=quizType.description,
                    )
                    for quizType in quizeTypes
                ]
            ),
            records=[
                StudyRecordsResponse(
                    user_answer_id=answer.quizId,
                    score=answer.aiEvaluation.score,
                    question=next(
                        (
                            quiz.question
                            for quiz in quizzes
                            if quiz.quizId == answer.quizId
                        ),
                        "",
                    ),
                    quiz_type_id=next(
                        (
                            quiz.quizTypeId
                            for quiz in quizzes
                            if quiz.quizId == answer.quizId
                        ),
                        uuid4(),
                    ),
                    # ダミーで現在日時
                    answered_at=datetime.date.today(),
                    answer_time_minutes=3,  # ダミーで3分
                    answer_time_seconds=20,  # ダミーで20秒
                    is_completed_review=any(
                        schedule.quizId == answer.quizId for schedule in reviewSchedules
                    ),
                )
                for answer in userAnswers
            ],
        )

    async def get_study_record(
        self, user_id: UUID, user_answer_id: UUID
    ) -> QuizStudyRecordResponse:
        """クイズの学習履歴単体を取得する。"""
        userAnswer = await self.userAnswerRepository.getById(user_id)

        quiz = await self.quizRepository.getById(userAnswer.quizId)

        # クイズに紐づく学習履歴一覧を取得する
        userAnswers = await self.userAnswerRepository.getAllByQuizIdUserId(
            user_id, quiz.quizId
        )

        return QuizStudyRecordResponse(
            user_answers=[
                UserAnswerResponse(
                    user_answer=answer.answer,
                    ai_evaluation_score=answer.aiEvaluation.score,
                    answered_at=datetime.date.today(),  # ダミーで現在日時
                    ai_feedback=answer.aiEvaluation.feedback,
                )
                for answer in userAnswers
            ],
            quiz=QuizResponse(
                id=quiz.quizId,
                content=quiz.question,
                type=next(
                    (
                        quiz_type.name
                        for quiz_type in await self.quiZTypeRepository.getAll()
                        if quiz_type.quizTypeId == quiz.quizTypeId
                    ),
                    "",
                ),
                difficulty=quiz.difficulty.name,
            ),
        )

    async def create_quiz_answer(
        self, request: QuizAnswerRequest, user_id: UUID
    ) -> QuizAnswerResponse:
        """クイズの回答を添削する。"""

        # クイズを取得する
        quiz = await self.quizRepository.getById(request.quiz_id)

        # ユーザーの回答を添削する
        evaluation: AIEvaluationValueObject = (
            await self.aiAPIRepository.get_ai_evaluation(
                question=quiz.question,
                userAnswer=request.user_answer,
            )
        )

        # エンティティを作成する
        user_answer_entity = UserAnswerEntity(
            userAnswerId=uuid4(),
            userId=user_id,
            quizId=quiz.quizId,
            answer=request.user_answer,
            aiEvaluation=evaluation,
        )

        # ユーザーの回答、及びAIの回答を保存する
        await self.userAnswerRepository.create(userAnswerEntity=user_answer_entity)

        return QuizAnswerResponse(
            score=evaluation.score,
            user_answer=request.user_answer,
            ai_model_answer=evaluation.modelAnswer,
            ai_feedback=evaluation.feedback,
        )
