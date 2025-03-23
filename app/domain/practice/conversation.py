import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ConversationEntity(BaseModel):
    id: UUID = Field(..., description="id")
    user_id : UUID = Field(..., description="user id")
    title: str = Field(...,min_length=1,max_length=200, description="title")
    created_at: datetime.datetime = Field(..., description="created at")