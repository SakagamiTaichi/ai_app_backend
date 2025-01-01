from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.schemas.recipe import Recipe
from app.core.config import settings

class RecipeGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE
        )

    def generate_recipe(self, ingredients: List[str]) -> Recipe:
        input_ingredient = ", ".join(ingredients)
        prompt = ChatPromptTemplate.from_template(
            "与えられた食材を使用して作ることができる料理のレシピを生成してください。\n"
            "要件:\n"
            "1. 指定された食材を必ず全て使用すること\n"
            "2. レシピは以下の要素を含むこと:\n"
            "   - 料理名\n"
            "   - 材料リスト（分量付き）\n"
            "   - 詳細な調理手順\n"
            "3. 一般家庭で実現可能なレシピであること\n"
            "4. 調理手順は具体的で分かりやすく記述すること\n"
            "\n"
            "メイン食材: {ingredient}"
        )
        chain = prompt | self.llm.with_structured_output(Recipe)
        return chain.invoke({"ingredient": input_ingredient})