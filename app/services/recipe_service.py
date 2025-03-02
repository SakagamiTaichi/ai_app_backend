# from datetime import datetime
# from typing import List
# from urllib.parse import urlparse
# from uuid import UUID
# import uuid
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
# import requests
# from app.schemas.recipe import Ingredient, Recipe, RecipeHistories, RecipeHistory, RecipeHistoryDetail, RecipeResponse, get_current_jst_time
# from supabase import create_client
# from app.core.config import settings
# from openai import OpenAI
# import os


# class RecipeService:
#     def __init__(self):
#         self.llm = ChatOpenAI(
#             model=settings.OPENAI_MODEL,
#             temperature=settings.TEMPERATURE
#         )
#         self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
#         self.image_generator = RecipeImageGenerator()
#         self.openai = OpenAI()
    
#     def upload_image(self, file_path:str) -> str:
#         """画像をアップロードする関数"""
#         try:
#             bucket_name = "ai-images"
#             response = requests.get(file_path)
#             if response.status_code == 200:
#                 # URLからファイル名を取得
#                 file_name = os.path.basename(urlparse(file_path).path)
#                 if not file_name:  # ファイル名が取得できない場合
#                     file_name = "temp_image.png"
                
#                 # 一時ファイルとして保存
#                 temp_path = f"temp_{file_name}"
#                 with open(temp_path, 'wb') as f:
#                     f.write(response.content)
                
#                 # 一時ファイルをアップロード
#                 with open(temp_path, 'rb') as f:
#                     response = self.client.storage.from_(bucket_name).upload(
#                         path=file_name, 
#                         file=f
#                     )
                
#                 # 一時ファイルを削除
#                 os.remove(temp_path)

#             # アップロードされたファイルのURLを取得
#             file_url = self.client.storage.from_(bucket_name).get_public_url(file_name)
#             return file_url
        
#         except Exception as e:
#             print(f"アップロードエラー: {str(e)}")
#             return None     

#     def generate_recipe(self, ingredients: List[str]) -> Recipe:
#         input_ingredient = ", ".join(ingredients)
#         prompt = ChatPromptTemplate.from_template(
#             "与えられた食材を使用して作ることができる料理のレシピを生成してください。\n"
#             "要件:\n"
#             "1. 指定された食材を必ず全て使用すること\n"
#             "2. レシピは以下の要素を含むこと:\n"
#             "   - 料理名\n"
#             "   - 材料リスト（分量付き）\n"
#             "   - 詳細な調理手順\n"
#             "3. 一般家庭で実現可能なレシピであること\n"
#             "4. 調理手順は具体的で分かりやすく記述すること\n"
#             "5. レシピのコツや注意事項があれば記載すること\n"
#             "\n"
#             "メイン食材: {ingredient}"
#         )
#         chain = prompt | self.llm.with_structured_output(RecipeResponse)
#         generated_recipe = chain.invoke({"ingredient": input_ingredient})

#         image_data = self.image_generator.generate_image(generated_recipe)


        
#         if image_data:
#             image_url = self.upload_image(image_data)
#             # image_urlの最後の?を削除
#             image_url = image_url.split("?")[0]

#         # レシピのID
#         id = uuid.uuid4()
#         # 現在日本時刻
#         created_at = get_current_jst_time()

#         return_recipe = Recipe(
#             id=id,
#             dish_name=generated_recipe.dish_name,
#             ingredients=generated_recipe.ingredients,
#             steps=generated_recipe.steps,
#             tips=generated_recipe.tips,
#             created_at=created_at,
#             image_url=image_url
#         )

#         # 生成されたレシピをSuparbaseに保存する

#         try:

#             # 1. recipeテーブルにメインレコードを挿入
#             recipe_data = {
#                 "id": str(id),  # UUIDを文字列に変換
#                 "dish_name": generated_recipe.dish_name,
#                 "created_at": created_at.isoformat(),
#                 "image_url": image_url
#             }
#             recipe_response = self.client.table('recipe').insert(recipe_data).execute()
            
#             # 2. recipe_ingredientsテーブルに材料を挿入
#             ingredients_data = [
#                 {
#                     "recipe_id": str(id),
#                     "name": ingredient.name,
#                     "amount": ingredient.amount
#                 }
#                 for ingredient in generated_recipe.ingredients
#             ]
#             ingredients_response = self.client.table('recipe_ingredients').insert(ingredients_data).execute()
            
#             # 3. recipe_stepsテーブルに手順を挿入
#             steps_data = [
#                 {
#                     "recipe_id": str(id),
#                     "step": step
#                 }
#                 for step in generated_recipe.steps
#             ]
#             steps_response = self.client.table('recipe_steps').insert(steps_data).execute()

#             #4. recipe_tipsテーブルにコツや注意事項を挿入
#             tips_data = [
#                 {
#                     "recipe_id": str(id),
#                     "tip": tip
#                 }
#                 for tip in generated_recipe.tips
#             ]

#             tips_response = self.client.table('recipe_tips').insert(tips_data).execute()
            
#         except Exception as e:
#             # エラーが発生した場合は適切なエラーハンドリングを行う
#             print(f"Error storing recipe in Supabase: {str(e)}")
#             # 必要に応じてエラーを上位に伝播させる
#             raise


#         return return_recipe
    
    
#     def get_recipe_histories(self) -> RecipeHistories:
#         """過去に生成されたレシピの一覧を取得します"""
#         try:
#             # recipeテーブルから全レコードを取得（作成日時の降順）
#             response = self.client.table('recipe') \
#                 .select('*') \
#                 .order('created_at', desc=True) \
#                 .execute()

#             # レスポンスから履歴リストを作成
#             histories = [
#                 RecipeHistory(
#                     id=UUID(record['id']),
#                     dish_name=record['dish_name'],
#                     created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
#                 )
#                 for record in response.data
#             ]

#             return RecipeHistories(recipe_histories=histories)

#         except Exception as e:
#             print(f"Error fetching recipe histories: {str(e)}")
#             raise

#     def get_recipe_detail(self, recipe_id: UUID) -> RecipeHistoryDetail:
#         """指定されたIDのレシピの詳細情報を取得します"""
#         try:
#             # レシピの基本情報を取得
#             recipe_response = self.client.table('recipe') \
#                 .select('*') \
#                 .eq('id', str(recipe_id)) \
#                 .single() \
#                 .execute()

#             if not recipe_response.data:
#                 raise ValueError(f"Recipe with id {recipe_id} not found")

#             # 材料情報を取得
#             ingredients_response = self.client.table('recipe_ingredients') \
#                 .select('*') \
#                 .eq('recipe_id', str(recipe_id)) \
#                 .execute()

#             # 手順情報を取得
#             steps_response = self.client.table('recipe_steps') \
#                 .select('*') \
#                 .eq('recipe_id', str(recipe_id)) \
#                 .order('id') \
#                 .execute()
            
#             # レシピのコツや注意事項を取得
#             tips_response = self.client.table('recipe_tips') \
#                 .select('*') \
#                 .eq('recipe_id', str(recipe_id)) \
#                 .execute()
            

#             # 材料リストを作成
#             ingredients = [
#                 Ingredient(
#                     name=ing['name'],
#                     amount=ing['amount']
#                 )
#                 for ing in ingredients_response.data
#             ]

#             # 手順リストを作成
#             steps = [step['step'] for step in steps_response.data]

#             # レシピのコツや注意事項リストを作成
#             tips = [tip['tip'] for tip in tips_response.data]

#             # RecipeHistoryDetailモデルを作成して返す
#             return RecipeHistoryDetail(
#                 id=UUID(recipe_response.data['id']),
#                 dish_name=recipe_response.data['dish_name'],
#                 ingredients=ingredients,
#                 steps=steps,
#                 tips=tips,
#                 created_at=datetime.fromisoformat(recipe_response.data['created_at'].replace('Z', '+00:00')),
#                 image_url=recipe_response.data['image_url']
#             )

#         except Exception as e:
#             print(f"Error fetching recipe detail: {str(e)}")
#             raise

# class RecipeImageGenerator:
#     def __init__(self):
#         self.openAI = OpenAI()

#     def generate_image(self, recipe: RecipeResponse) -> str:
#         # プロンプトの生成
#         # prompt = self._create_image_prompt(recipe)

#         prompt = f"""
#         完成した料理の写真: {recipe.dish_name}。
#         プロフェッショナルな料理写真のように、美しく盛り付けられ、
#         鮮やかで食欲をそそる見た目。
#         クリアで高品質な画像。
#         料理以外のオブジェクトは表示しない
#         """
        
#         # 画像の生成
#         try:
#             response = self.openAI.images.generate(
#               model="dall-e-3",
#               prompt=prompt,
#               size="1792x1024",
#               quality="standard",
#               response_format="url",
#               n=1,
#             )
#             img_str = response.data[0].url
            
#             return img_str
            
#         except Exception as e:
#             print(f"画像生成中にエラーが発生しました: {str(e)}")
#             return None