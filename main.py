from fastapi import FastAPI, Query, Path, HTTPException
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# FastAPIインスタンスの作成
app = FastAPI(
    title="Sample API",
    description="FastAPIの基本機能を学ぶためのサンプルAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのオリジン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

# 商品カテゴリーの列挙型を定義
class CategoryEnum(str, Enum):
    electronics = "electronics"
    books = "books"
    clothing = "clothing"

# レスポンスモデルの定義
class Product(BaseModel):
    id: int
    name: str
    price: float
    category: CategoryEnum
    description: Optional[str] = None

# サンプルデータ
sample_products = [
    Product(id=1, name="Laptop", price=999.99, category=CategoryEnum.electronics),
    Product(id=2, name="Python Book", price=29.99, category=CategoryEnum.books),
    Product(id=3, name="T-shirt", price=19.99, category=CategoryEnum.clothing)
]

# ルートパス
@app.get("/")
async def root():
    return {"message": "Welcome to Sample API"}

#AIレシピの取得
# @app.post("/recipe/",response_model=Recipe)
# async def generate_recipe(
#     ingredients: List[str] = Query(..., min_length=1, description="食材のリスト")
# ):
#     recipe = recipe_generator.run(ingredients)
#     return recipe


# 全商品の取得
@app.get("/products/", response_model=list[Product])
async def get_products(
    category: Optional[CategoryEnum] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0)
):
    filtered_products = sample_products

    # カテゴリーでフィルタリング
    if category:
        filtered_products = [p for p in filtered_products if p.category == category]
    
    # 価格でフィルタリング
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p.price >= min_price]
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.price <= max_price]

    return filtered_products

# 特定の商品の取得
@app.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: int = Path(..., ge=1, description="取得する商品のID")
):
    for product in sample_products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")