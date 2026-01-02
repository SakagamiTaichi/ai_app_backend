import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class QuizTypeResponse(BaseModel):
    """クイズの種類を表すモデル"""

    id: Optional[UUID] = Field(..., description="クイズの種類ID")
    name: str = Field(..., description="クイズの種類名")
    description: str = Field(..., description="クイズの種類の説明")


class QuizTypesResponse(BaseModel):
    """クイズの種類のレスポンスモデル"""

    quiz_types: List[QuizTypeResponse] = Field(..., description="クイズの種類のリスト")


class QuizResponse(BaseModel):
    """クイズのレスポンスモデル"""

    id: UUID = Field(..., description="クイズID")
    content: str = Field(..., description="クイズの内容")
    type: str = Field(..., description="クイズの種類名")
    difficulty: str = Field(..., description="クイズの難易度名")


class StudyRecordsResponse(BaseModel):
    """学習履歴のレスポンスモデル"""

    user_answer_id: UUID = Field(..., description="ユーザーの回答ID")
    score: int = Field(..., description="スコア")
    question: str = Field(..., description="クイズの問題文")
    quiz_type_id: UUID = Field(..., description="クイズの種類ID")
    answered_at: datetime.datetime = Field(..., description="回答日時")
    answer_time_minutes: int = Field(..., description="回答にかかった時間（分）")
    answer_time_seconds: int = Field(..., description="回答にかかった時間（秒）")
    is_completed_review: bool = Field(..., description="復習が完了しているかどうか")


class QuizStudyRecordsResponse(BaseModel):
    """クイズの学習履歴のレスポンスモデル"""

    records: List[StudyRecordsResponse] = Field(..., description="学習履歴のリスト")
    quiz_types: List[QuizTypeResponse] = Field(..., description="クイズの種類のリスト")


class UserAnswerResponse(BaseModel):
    """ユーザーの回答のレスポンスモデル"""

    user_answer: str = Field(..., description="ユーザーの回答")
    ai_evaluation_score: int = Field(..., description="スコア")
    answered_at: datetime.datetime = Field(..., description="回答日時")
    ai_feedback: str = Field(..., description="AIからのフィードバック")
    ai_model_answer: str = Field(..., description="AIの模範回答")


class QuizStudyRecordResponse(BaseModel):
    """学習履歴単体のレスポンスモデル"""

    user_answers: List[UserAnswerResponse] = Field(
        ..., description="ユーザーの回答のリスト"
    )
    quiz: QuizResponse = Field(..., description="クイズの情報")


class QuizAnswerRequest(BaseModel):
    """クイズの回答のリクエストモデル"""

    user_answer: str = Field(..., description="ユーザーの回答")
    quiz_id: UUID = Field(..., description="クイズID")


class QuizAnswerResponse(BaseModel):
    """クイズの回答のレスポンスモデル"""

    score: int = Field(..., description="スコア")
    user_answer: str = Field(..., description="ユーザーの回答")
    ai_model_answer: str = Field(..., description="AIモデルの回答")
    ai_feedback: str = Field(..., description="AIからのフィードバック")
