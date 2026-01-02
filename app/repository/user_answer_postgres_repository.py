from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.userAnswer.user_answer_entity import UserAnswerEntity
from app.domain.userAnswer.user_answer_repository import UserAnswerRepository
from app.domain.userAnswer.ai_evaluation_value_object import AIEvaluationValueObject
from app.schema.models import UserAnswers


class UserAnswerPostgresRepository(UserAnswerRepository):
    """PostgreSQLを使用したユーザーの回答のリポジトリ実装"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def getById(self, userAnswerId: UUID) -> UserAnswerEntity:
        """指定されたユーザー回答IDに紐づくユーザーの回答を取得する"""
        try:
            stmt = select(UserAnswers).where(UserAnswers.user_answer_id == userAnswerId)
            result = await self.db.execute(stmt)
            user_answer = result.scalar_one_or_none()

            if user_answer is None:
                raise ValueError("User answer not found")

            return UserAnswerEntity(
                userAnswerId=user_answer.user_answer_id,  # type: ignore
                userId=user_answer.user_id,  # type: ignore
                quizId=user_answer.quiz_id,  # type: ignore
                answer=user_answer.answer,  # type: ignore
                aiEvaluation=AIEvaluationValueObject(
                    score=user_answer.score,  # type: ignore
                    feedback=user_answer.feedback or "",  # type: ignore
                    modelAnswer=user_answer.model_answer or "",  # type: ignore
                ),
                answeredAt=user_answer.created_at,  # type: ignore
            )
        except Exception as e:
            raise e

    async def getAllByUserId(self, userId: UUID) -> List[UserAnswerEntity]:
        """指定されたユーザーIDに紐づく全てのクイズ回答を取得する"""
        try:
            stmt = select(UserAnswers).where(UserAnswers.user_id == userId)
            result = await self.db.execute(stmt)
            user_answers = result.scalars().all()

            return [
                UserAnswerEntity(
                    userAnswerId=user_answer.user_answer_id,  # type: ignore
                    userId=user_answer.user_id,  # type: ignore
                    quizId=user_answer.quiz_id,  # type: ignore
                    answer=user_answer.answer,  # type: ignore
                    aiEvaluation=AIEvaluationValueObject(
                        score=user_answer.score,  # type: ignore
                        feedback=user_answer.feedback or "",  # type: ignore
                        modelAnswer=user_answer.model_answer or "",  # type: ignore
                    ),
                    answeredAt=user_answer.created_at,  # type: ignore
                )
                for user_answer in user_answers
            ]
        except Exception as e:
            raise

    async def getAllByQuizIdUserId(
        self, userId: UUID, quizId: UUID
    ) -> List[UserAnswerEntity]:
        """ユーザーとクイズに紐づく全てのクイズ回答を取得する"""
        try:
            stmt = select(UserAnswers).where(
                UserAnswers.user_id == userId, UserAnswers.quiz_id == quizId
            )
            result = await self.db.execute(stmt)
            user_answers = result.scalars().all()

            return [
                UserAnswerEntity(
                    userAnswerId=user_answer.user_answer_id,  # type: ignore
                    userId=user_answer.user_id,  # type: ignore
                    quizId=user_answer.quiz_id,  # type: ignore
                    answer=user_answer.answer,  # type: ignore
                    aiEvaluation=AIEvaluationValueObject(
                        score=user_answer.score,  # type: ignore
                        feedback=user_answer.feedback or "",  # type: ignore
                        modelAnswer=user_answer.model_answer or "",  # type: ignore
                    ),
                    answeredAt=user_answer.created_at,  # type: ignore
                )
                for user_answer in user_answers
            ]
        except Exception as e:
            raise e

    async def create(self, userAnswerEntity: UserAnswerEntity) -> None:
        """ユーザーの回答を新規作成する"""
        try:
            new_user_answer = UserAnswers(
                user_answer_id=userAnswerEntity.userAnswerId,
                user_id=userAnswerEntity.userId,
                quiz_id=userAnswerEntity.quizId,
                answer=userAnswerEntity.answer,
                score=userAnswerEntity.aiEvaluation.score,
                feedback=userAnswerEntity.aiEvaluation.feedback,
                model_answer=userAnswerEntity.aiEvaluation.modelAnswer,
            )
            self.db.add(new_user_answer)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e
