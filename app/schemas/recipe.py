# import datetime
# from pydantic import BaseModel, Field
# from typing import List
# import uuid
# from uuid import UUID

# import pytz

# def get_current_jst_time():
#     return datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

# class Ingredient(BaseModel):
#     name: str = Field(..., description="材料名")
#     amount: str = Field(..., description="必要な量")

# class RecipeResponse(BaseModel):
#     dish_name: str = Field(..., description="料理名")
#     ingredients: List[Ingredient] = Field(..., description="材料と量のリスト")
#     steps: List[str] = Field(..., description="調理手順のリスト")
#     tips: List[str] = Field(...,  description="レシピのコツや注意事項")

# class Recipe(BaseModel):
#     id: UUID = Field(default_factory=uuid.uuid4, description="レシピの一意識別子")
#     dish_name: str = Field(..., description="料理名")
#     ingredients: List[Ingredient] = Field(..., description="材料と量のリスト")
#     steps: List[str] = Field(..., description="調理手順のリスト")
#     tips: List[str] = Field(..., description="レシピのコツや注意事項")
#     # 作成時刻を日本時刻で取得するように修正
#     created_at: datetime.datetime = Field(...,description="レシピが生成された日時")
#     image_url: str = Field(..., description="料理の画像URL")

# class RecipeRequest(BaseModel):
#     ingredients: List[str] = Field(..., description="レシピ生成に使用する食材リスト")

# class RecipeHistory(BaseModel):
#     id: UUID = Field(..., description="レシピの一意識別子")
#     dish_name: str = Field(..., description="料理名")
#     created_at: datetime.datetime = Field(..., description="レシピが生成された日時")

# class RecipeHistories(BaseModel):
#     recipe_histories: List[RecipeHistory] = Field(..., description="過去に生成されたレシピのリスト")

# class RecipeHistoryDetail(BaseModel):
#     id: UUID = Field(default_factory=uuid.uuid4, description="レシピの一意識別子")
#     dish_name: str = Field(..., description="料理名")
#     ingredients: List[Ingredient] = Field(..., description="材料と量のリスト")
#     steps: List[str] = Field(..., description="調理手順のリスト")
#     tips: List[str] = Field("", description="レシピのコツや注意事項")
#     created_at: datetime.datetime = Field(..., description="レシピが生成された日時")
#     image_url: str = Field("", description="料理の画像URL")