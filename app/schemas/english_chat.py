import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description="user input message")

class ChatResponse(BaseModel):
    content: str = Field(..., description="AI response")

class ConversationSet(BaseModel):
    id: UUID = Field(..., description="id")
    user_id : UUID = Field(..., description="user id")
    title: str = Field(..., description="title")
    created_at: datetime.datetime = Field(..., description="created at")

class ConversationSetCreate(BaseModel):
    title: str = Field(..., description="会話セットのタイトル")

class Message(BaseModel):
    set_id: UUID = Field(..., description="set id")
    message_order: int = Field(..., description="message order")
    speaker_number: int = Field(..., description="speaker number")
    message_en: str = Field(..., description="message in english")
    message_ja: str = Field(..., description="message in japanese")
    created_at: datetime.datetime = Field(..., description="created at")

class MessageCreate(BaseModel):
    set_id: UUID = Field(..., description="会話セットID")
    message_order: int = Field(..., description="メッセージの順序")
    speaker_number: int = Field(..., description="話者番号")
    message_en: str = Field(..., description="英語でのメッセージ")
    message_ja: str = Field(..., description="日本語でのメッセージ")

class MessageTestResultUserAnswerRequest(BaseModel):
    user_answer: str = Field(..., description="ユーザーの解答")
    correct_answer: str = Field(..., description="英語の答案")



class MessageTestResult(BaseModel):
    user_anser: str = Field(..., description="ユーザーの解答(HTML)")
    correct_answer: str = Field(..., description="英語の答案(HTML)")
    is_correct: bool = Field(..., description="正解かどうか")
    similarity_to_correct: float = Field(..., description="正解との類似度")


class MessageTestResultSummary(BaseModel):
    correct_count: int = Field(..., description="正解数")
    total_count: int = Field(..., description="総問題数")
    correct_rate: float = Field(..., description="正解率")
    result : List[MessageTestResult] = Field(..., description="テスト結果")
    # 前回の結果
    last_correct_rate: float | None = Field(..., description="前回の正解率")