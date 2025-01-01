from pydantic import BaseModel, Field

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description="ユーザーの入力メッセージ")

class ChatResponse(BaseModel):
    content: str = Field(..., description="チャットボットの応答")