from typing import List
from pydantic import BaseModel, Field


class GeneratedMessageValueObject(BaseModel):
    message_en: str = Field(..., description="英語のメッセージ")
    message_ja: str = Field(..., description="日本語のメッセージ")


class GeneratedConversationValueObject(BaseModel):
    title: str = Field(..., description="日本語の会話のタイトル")
    messages: List[GeneratedMessageValueObject] = Field(
        ..., description="会話セットのメッセージ一覧"
    )
