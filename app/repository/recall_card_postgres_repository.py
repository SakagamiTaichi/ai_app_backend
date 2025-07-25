from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from app.domain.recall.reacall_card_entity import RecallCardEntity
from app.domain.recall.recall_card_repository import RecallCardrepository
from app.schema.models import RecallCards


class RecallCardPostgresRepository(RecallCardrepository):
    """PostgreSQLを使用した練習機能のリポジトリ実装"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def getAllByUserId(self, user_id: str) -> List[RecallCardEntity]:
        """全ての復習カードを取得する"""
        try:
            result = await self.db.execute(
                select(RecallCards)
                .where(RecallCards.user_id == user_id)
                .order_by(desc(RecallCards.created_at))
            )

            recall_cards = result.scalars().all()
            return [
                RecallCardEntity(
                    id=recall_card.recall_card_id,  # type: ignore
                    userId=recall_card.user_id,  # type: ignore
                    question=recall_card.question,  # type: ignore
                    answer=recall_card.answer,  # type: ignore
                    correctPoint=recall_card.correct_point,  # type: ignore
                    reviewDeadline=recall_card.review_deadline,  # type: ignore
                    created_at=recall_card.created_at,  # type: ignore
                )
                for recall_card in recall_cards
            ]
        except Exception as e:
            raise

    async def getByRecallCardIdAndUserId(
        self, recall_card_id: UUID, user_id: UUID
    ) -> Optional[RecallCardEntity]:
        """復習カードIDに紐づく復習カードを取得する"""
        try:
            result = await self.db.execute(
                select(RecallCards)
                .where(RecallCards.recall_card_id == recall_card_id)
                .where(RecallCards.user_id == user_id)
            )
            recall_card = result.scalar_one_or_none()
            if recall_card:
                return RecallCardEntity(
                    recallCardId=recall_card.recall_card_id,  # type: ignore
                    userId=recall_card.user_id,  # type: ignore
                    question=recall_card.question,  # type: ignore
                    answer=recall_card.answer,  # type: ignore
                    correctPoint=recall_card.correct_point,  # type: ignore
                    reviewDeadline=recall_card.review_deadline,  # type: ignore
                )
            return None
        except Exception as e:
            raise

    async def getMostOverdueDeadline(self, user_id: UUID) -> Optional[RecallCardEntity]:
        """期限が最も過ぎている復習カードを1つだけ取得する"""
        try:
            result = await self.db.execute(
                select(RecallCards)
                .where(RecallCards.user_id == user_id)
                .order_by(RecallCards.review_deadline)
                .limit(1)
            )
            recall_card = result.scalar_one_or_none()
            if recall_card:
                return RecallCardEntity(
                    recallCardId=recall_card.recall_card_id,  # type: ignore
                    userId=recall_card.user_id,  # type: ignore
                    question=recall_card.question,  # type: ignore
                    answer=recall_card.answer,  # type: ignore
                    correctPoint=recall_card.correct_point,  # type: ignore
                    reviewDeadline=recall_card.review_deadline,  # type: ignore
                )
            return None
        except Exception as e:
            raise

    async def updateAll(self, recall_cards: List[RecallCardEntity]) -> None:
        """復習カードを更新する"""
        try:
            for recall_card in recall_cards:
                stmt = (
                    update(RecallCards)
                    .where(RecallCards.recall_card_id == recall_card.recallCardId)
                    .values(
                        question=recall_card.question,
                        answer=recall_card.answer,
                        correct_point=recall_card.correctPoint,
                        review_deadline=recall_card.reviewDeadline,
                    )
                )
                await self.db.execute(stmt)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update recall cards",
            ) from e

    async def createAll(self, recall_cards: List[RecallCardEntity]) -> None:
        """復習カードを作成する"""
        try:
            models = [
                RecallCards(
                    recall_card_id=recall_card.recallCardId,
                    user_id=recall_card.userId,
                    question=recall_card.question,
                    answer=recall_card.answer,
                    correct_point=recall_card.correctPoint,
                    review_deadline=recall_card.reviewDeadline,
                )
                for recall_card in recall_cards
            ]
            self.db.add_all(models)
            await self.db.commit()
        except Exception as e:
            raise
