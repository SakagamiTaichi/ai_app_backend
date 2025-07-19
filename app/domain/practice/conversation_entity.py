import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MessageEntity(BaseModel):
    conversationId: UUID = Field(..., description="会話セットID")
    messageOrder: int = Field(..., description="メッセージの順序")
    speakerNumber: int = Field(..., description="話者番号")
    messageEn: str = Field(..., description="英語でのメッセージ")
    messageJa: str = Field(..., description="日本語でのメッセージ")
    createdAt: datetime.datetime = Field(..., description="created at")


class ConversationEntity(BaseModel):
    id: UUID = Field(..., description="id")
    userId: UUID = Field(..., description="user id")
    title: str = Field(..., min_length=1, max_length=200, description="title")
    createdAt: datetime.datetime = Field(..., description="created at")
    order: int = Field(..., description="order")
    messages: list[MessageEntity] = Field(..., description="会話セットのメッセージ一覧")
