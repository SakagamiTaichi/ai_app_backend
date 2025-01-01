
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from openai import BaseModel

class TextToSQLRequest(BaseModel):
    message: str = Field(..., description="ユーザーの入力メッセージ")

class Column(BaseModel):
    """テーブルのカラムを表現するモデル"""
    field: str = Field(...,description="カラム名")
    headerName: str = Field(...,description="カラムのヘッダー名")
    width: int = Field(...,description="カラムに必要と思われる幅")

class TableData(BaseModel):
    """テーブル形式のデータを表現するモデル"""
    columns: List[Column] = Field(...,description="テーブルのカラム名のリスト")
    rows: List[Dict[str, Any]] = Field(...,description="各行のデータを含む辞書のリスト")