from pydantic import BaseModel, Field


class AIEvaluationValueObject(BaseModel):
    score: int = Field(..., ge=0, le=100, description="AI評価スコア")
    feedback: str = Field(
        ..., min_length=1, max_length=300, description="フィードバック"
    )
    modelAnswer: str = Field(..., min_length=1, max_length=300, description="模範解答")
