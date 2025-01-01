from pydantic import BaseModel, Field
from typing import List

class Ingredient(BaseModel):
    name: str = Field(..., description="材料名")
    amount: str = Field(..., description="必要な量")

class Recipe(BaseModel):
    dish_name: str = Field(..., description="料理名")
    ingredients: List[Ingredient] = Field(..., description="材料と量のリスト")
    steps: List[str] = Field(..., description="調理手順のリスト")

    @property
    def text(self) -> str:
        ingredients_text = "\n".join([f"- {ing.name} {ing.amount}" for ing in self.ingredients])
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(self.steps)])
        
        return f"""料理名: {self.dish_name}

材料:
{ingredients_text}

作り方:
{steps_text}"""

class RecipeRequest(BaseModel):
    ingredients: List[str] = Field(..., description="レシピ生成に使用する食材リスト")