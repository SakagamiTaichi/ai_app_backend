from uuid import UUID
from pydantic import BaseModel, Field


class NextRecallCardResponse(BaseModel):
    """次の暗記カードのレスポンス"""

    recall_card_id: UUID = Field(..., description="暗記カードID")
    question: str = Field(..., description="問題文")


class RecallCardAnswerRequest(BaseModel):
    """暗記カードの回答リクエスト"""

    recall_card_id: UUID = Field(..., description="暗記カードID")
    answer: str = Field(..., description="回答内容")
