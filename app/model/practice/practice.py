import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="user input message")

class ChatResponse(BaseModel):
    content: str = Field(..., description="AI response")

class Conversation(BaseModel):
    id: UUID = Field(..., description="id")
    user_id : UUID = Field(..., description="user id")
    title: str = Field(..., description="title")
    created_at: datetime.datetime = Field(..., description="created at")

class ConversationsResponse(BaseModel):
    conversations: List[Conversation] = Field(..., description="conversation")

class ConversationSetCreate(BaseModel):
    title: str = Field(..., description="会話セットのタイトル")

class MessageResponse(BaseModel):
    conversation_id: UUID = Field(..., description="set id")
    message_order: int = Field(..., description="message order")
    speaker_number: int = Field(..., description="speaker number")
    message_en: str = Field(..., description="message in english")
    message_ja: str = Field(..., description="message in japanese")
    created_at: datetime.datetime = Field(..., description="created at")

class ConversationResponse(BaseModel):
    messages :List[MessageResponse] = Field(..., description="会話セットのメッセージ一覧")

class MessageCreate(BaseModel):
    conversation_id: UUID = Field(..., description="会話セットID")
    message_order: int = Field(..., description="メッセージの順序")
    speaker_number: int = Field(..., description="話者番号")
    message_en: str = Field(..., description="英語でのメッセージ")
    message_ja: str = Field(..., description="日本語でのメッセージ")

class RecallTestAnswer(BaseModel):
    message_order: int = Field(..., description="メッセージの順序")
    user_answer: str = Field(..., description="ユーザーの解答")

class RecallTestRequest(BaseModel):
    conversation_id: UUID = Field(..., description="会話セットID")
    answers: List[RecallTestAnswer] = Field(..., description="テストの解答")

class MessageTestResult(BaseModel):
    message_order: int = Field(..., description="メッセージの順序")
    user_answer: str = Field(..., description="ユーザーの解答(HTML)")
    correct_answer: str = Field(..., description="英語の答案(HTML)")
    is_correct: bool = Field(..., description="正解かどうか")
    similarity_to_correct: float = Field(..., description="正解との類似度")
    last_similarity_to_correct: float | None = Field(..., description="前回の正解との類似度")


class MessageTestResultSummary(BaseModel):
    correct_rate: float = Field(..., description="正解率")
    last_correct_rate: float | None = Field(..., description="前回の正解率")
    result : List[MessageTestResult] = Field(..., description="テスト結果")


