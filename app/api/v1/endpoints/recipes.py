from fastapi import APIRouter, HTTPException
from app.schemas.recipe import Recipe, RecipeRequest
from app.services.recipe_service import RecipeGenerator

router = APIRouter(prefix="/recipes", tags=["recipes"])
recipe_generator = RecipeGenerator()

@router.post("/generate", response_model=Recipe)
async def generate_recipe(request: RecipeRequest) -> Recipe:
    try:
        recipe = recipe_generator.generate_recipe(request.ingredients)
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))