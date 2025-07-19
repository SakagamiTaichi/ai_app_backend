from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.quiz.quize_entity import QuizEntity, DifficultyEnum
from app.domain.quiz.quize_repostiroy import QuizRepository
from app.schema.models import Quiz


class QuizPostgresRepository(QuizRepository):
    """PostgreSQLを使用したクイズのリポジトリ実装"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def getById(self, quizId: UUID) -> QuizEntity:
        """指定されたIDのクイズを取得する"""
        try:
            stmt = select(Quiz).where(Quiz.quiz_id == quizId)
            result = await self.db.execute(stmt)
            quiz = result.scalar_one_or_none()

            if quiz is None:
                raise ValueError("Quiz not found")

            return QuizEntity(
                quizId=quiz.quiz_id,  # type: ignore
                question=quiz.question,  # type: ignore
                modelAnswer=quiz.model_answer,  # type: ignore
                quizTypeId=quiz.quiz_type_id,  # type: ignore
                difficulty=DifficultyEnum(quiz.difficulty),  # type: ignore
            )
        except Exception as e:
            raise e

    async def getAll(self) -> List[QuizEntity]:
        """全てのクイズを取得する"""
        try:
            stmt = select(Quiz)
            result = await self.db.execute(stmt)
            quizzes = result.scalars().all()

            return [
                QuizEntity(
                    quizId=quiz.quiz_id,  # type: ignore
                    question=quiz.question,  # type: ignore
                    modelAnswer=quiz.model_answer,  # type: ignore
                    quizTypeId=quiz.quiz_type_id,  # type: ignore
                    difficulty=DifficultyEnum(quiz.difficulty),  # type: ignore
                )
                for quiz in quizzes
            ]
        except Exception as e:
            raise
