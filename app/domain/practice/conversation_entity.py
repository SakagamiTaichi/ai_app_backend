import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MessageEntity(BaseModel):
    conversation_id: UUID = Field(..., description="会話セットID")
    message_order: int = Field(..., description="メッセージの順序")
    speaker_number: int = Field(..., description="話者番号")
    message_en: str = Field(..., description="英語でのメッセージ")
    message_ja: str = Field(..., description="日本語でのメッセージ")
    created_at: datetime.datetime = Field(..., description="created at")

class ConversationEntity(BaseModel):
    id: UUID = Field(..., description="id")
    user_id : UUID = Field(..., description="user id")
    title: str = Field(...,min_length=1,max_length=200, description="title")
    created_at: datetime.datetime = Field(..., description="created at")
    order: int = Field(..., description="order")
    messages : list[MessageEntity] = Field(..., description="会話セットのメッセージ一覧")