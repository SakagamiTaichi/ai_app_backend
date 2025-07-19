from uuid import UUID
from app.core.app_exception import NotFoundError

from app.domain.recall.recall_card_repository import RecallCardrepository

from app.endpoint.recall.recall_model import (
    NextRecallCardResponse,
    RecallCardAnswerRequest,
)


class RecallCardService:
    def __init__(self, repository: RecallCardrepository):
        self.dbRepository = repository

    async def get_next_recall_card(self, user_id: UUID) -> NextRecallCardResponse:
        """次の暗記カードを取得する"""

        recall_card = await self.dbRepository.getMostOverdueDeadline(user_id)
        if not recall_card:
            raise NotFoundError("次の暗記カードはありません。")

        return NextRecallCardResponse(
            recall_card_id=recall_card.recallCardId,
            question=recall_card.question,
        )

    async def update_recall_card(
        self, user_id: UUID, request: RecallCardAnswerRequest
    ) -> None:
        """暗記カードの回答を更新する"""
        recall_card_id = request.recall_card_id
        recall_card = await self.dbRepository.getByRecallCardIdAndUserId(
            request.recall_card_id, user_id=user_id
        )

        if not recall_card:
            raise NotFoundError("指定された暗記カードが見つかりません。")

        # 回答の更新
        new_recall_card = recall_card.update_by_user_answer(user_answer=request.answer)

        await self.dbRepository.updateAll([new_recall_card])
