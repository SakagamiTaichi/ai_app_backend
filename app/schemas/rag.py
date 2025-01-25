from typing import List
from uuid import UUID
from pydantic import BaseModel, Field


class InformationRequest(BaseModel):
    information: str = Field(..., description="情報")

class InformationResponse(BaseModel):
    id: UUID = Field(..., description="情報の一意の識別子")
    document: str = Field(..., description="情報")

class InformationsResponse(BaseModel):
    informations: List[InformationResponse] = Field(..., description="情報のリスト")