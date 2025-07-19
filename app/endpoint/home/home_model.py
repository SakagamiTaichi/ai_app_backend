from pydantic import BaseModel, Field


class HomeResponse(BaseModel):
    message: str = Field(..., description="ホームのメッセージ")
    continuous_learning_days: int = Field(..., description="連続学習日数")
    pending_review_count: int = Field(..., description="復習待ちのクイズ数")
    all_quiz_count: int = Field(..., description="全クイズ数")
    average_score: int = Field(..., description="平均スコア")
