from datetime import datetime
from typing import List
from uuid import UUID
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.schemas.recipe import Ingredient, Recipe, RecipeHistories, RecipeHistory, RecipeHistoryDetail
from app.core.config import settings
from app.core.config import settings
from supabase import create_client, Client
from app.core.config import settings
import pytz


class RecipeService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE
        )
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

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
        generated_recipe = chain.invoke({"ingredient": input_ingredient})

        # 生成されたレシピをSuparbaseに保存する

        try:

            # 1. recipeテーブルにメインレコードを挿入
            recipe_data = {
                "id": str(generated_recipe.id),  # UUIDを文字列に変換
                "dish_name": generated_recipe.dish_name,
                "created_at": generated_recipe.created_at.isoformat()
            }
            recipe_response = self.client.table('recipe').insert(recipe_data).execute()
            
            # 2. recipe_ingredientsテーブルに材料を挿入
            ingredients_data = [
                {
                    "recipe_id": str(generated_recipe.id),
                    "name": ingredient.name,
                    "amount": ingredient.amount
                }
                for ingredient in generated_recipe.ingredients
            ]
            ingredients_response = self.client.table('recipe_ingredients').insert(ingredients_data).execute()
            
            # 3. recipe_stepsテーブルに手順を挿入
            steps_data = [
                {
                    "recipe_id": str(generated_recipe.id),
                    "step": step
                }
                for step in generated_recipe.steps
            ]
            steps_response = self.client.table('recipe_steps').insert(steps_data).execute()
            
        except Exception as e:
            # エラーが発生した場合は適切なエラーハンドリングを行う
            print(f"Error storing recipe in Supabase: {str(e)}")
            # 必要に応じてエラーを上位に伝播させる
            raise


        return generated_recipe
    
    
    def get_recipe_histories(self) -> RecipeHistories:
        """過去に生成されたレシピの一覧を取得します"""
        try:
            # recipeテーブルから全レコードを取得（作成日時の降順）
            response = self.client.table('recipe') \
                .select('*') \
                .order('created_at', desc=True) \
                .execute()

            # レスポンスから履歴リストを作成
            histories = [
                RecipeHistory(
                    id=UUID(record['id']),
                    dish_name=record['dish_name'],
                    created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                )
                for record in response.data
            ]

            return RecipeHistories(recipe_histories=histories)

        except Exception as e:
            print(f"Error fetching recipe histories: {str(e)}")
            raise

    def get_recipe_detail(self, recipe_id: UUID) -> RecipeHistoryDetail:
        """指定されたIDのレシピの詳細情報を取得します"""
        try:
            # レシピの基本情報を取得
            recipe_response = self.client.table('recipe') \
                .select('*') \
                .eq('id', str(recipe_id)) \
                .single() \
                .execute()

            if not recipe_response.data:
                raise ValueError(f"Recipe with id {recipe_id} not found")

            # 材料情報を取得
            ingredients_response = self.client.table('recipe_ingredients') \
                .select('*') \
                .eq('recipe_id', str(recipe_id)) \
                .execute()

            # 手順情報を取得
            steps_response = self.client.table('recipe_steps') \
                .select('*') \
                .eq('recipe_id', str(recipe_id)) \
                .order('id') \
                .execute()

            # 材料リストを作成
            ingredients = [
                Ingredient(
                    name=ing['name'],
                    amount=ing['amount']
                )
                for ing in ingredients_response.data
            ]

            # 手順リストを作成
            steps = [step['step'] for step in steps_response.data]

            # RecipeHistoryDetailモデルを作成して返す
            return RecipeHistoryDetail(
                id=UUID(recipe_response.data['id']),
                dish_name=recipe_response.data['dish_name'],
                ingredients=ingredients,
                steps=steps,
                created_at=datetime.fromisoformat(recipe_response.data['created_at'].replace('Z', '+00:00'))
            )

        except Exception as e:
            print(f"Error fetching recipe detail: {str(e)}")
            raise        