from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.quizType.quiz_type_entity import QuizTypeEntity
from app.domain.quizType.quiz_type_repository import QuizTypeRepository
from app.schema.models import QuizType


class QuizTypePostgresRepository(QuizTypeRepository):
    """PostgreSQLを使用したクイズの種類のリポジトリ実装"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def getAll(self) -> List[QuizTypeEntity]:
        """全てのクイズの種類を取得する"""
        try:
            stmt = select(QuizType)
            result = await self.db.execute(stmt)
            quiz_types = result.scalars().all()
            
            return [
                QuizTypeEntity(
                    quizTypeId=quiz_type.quiz_type_id,  # type: ignore
                    name=quiz_type.name,  # type: ignore
                    description=quiz_type.description if quiz_type.description else ""  # type: ignore
                )
                for quiz_type in quiz_types
            ]
        except Exception as e:
            raise
