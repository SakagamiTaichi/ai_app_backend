# from typing import List
# from fastapi import APIRouter, HTTPException
# from app.schemas.recipe import Recipe, RecipeHistories, RecipeRequest
# from app.services.recipe_service import RecipeService

# router = APIRouter(prefix="/recipes", tags=["recipes"])
# recipe_service = RecipeService()

# @router.post("/generate", response_model=Recipe)
# async def generate_recipe(request: RecipeRequest) -> Recipe:
#     try:
#         recipe = recipe_service.generate_recipe(request.ingredients)
#         return recipe
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/recipe-history", response_model=RecipeHistories)
# async def get_recipe_history() -> List[Recipe]:
#     try:
#         recipes = recipe_service.get_recipe_histories()
#         return recipes
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/recipe-detail/{recipe_id}", response_model=Recipe)
# async def get_recipe_detail(recipe_id: str) -> Recipe:
#     try:
#         recipe = recipe_service.get_recipe_detail(recipe_id)
#         return recipe
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))