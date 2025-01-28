
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from openai import BaseModel
from pydantic import ConfigDict

from app.schemas.personal_information import PersonalInformation

class TextToSQLRequest(BaseModel):
    message: str = Field(..., description="ユーザーの入力メッセージ")

class Column(BaseModel):
    """テーブルのカラムを表現するモデル"""
    field: str = Field(...,description="カラム名")
    headerName: str = Field(...,description="カラムのヘッダー名")
    width: int = Field(...,description="カラムに必要と思われる幅")

class TableData(BaseModel):
    """テーブル形式のデータを表現するモデル"""
    sql : str = Field(...,description="生成したSQL文")
    columns: List[Column] = Field(...,description="テーブルのカラム名のリスト")
    rows: List[Dict[str, Any]] = Field(...,description="各行のデータを含む辞書のリスト")

class PersonalInformationResponse(BaseModel):
    """個人情報のレスポンスモデル"""
    informations : List[PersonalInformation] = Field(...,description="個人情報のリスト")