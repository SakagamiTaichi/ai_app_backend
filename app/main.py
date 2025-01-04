from fastapi import FastAPI
from app.api.v1.endpoints import chat, items, text_to_sql
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from app.api.v1.endpoints import recipes
from app.core.config import settings

# FastAPIインスタンスの作成
app = FastAPI(
    title="Sample API",
    description="FastAPIの基本機能を学ぶためのサンプルAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # フロントエンドのオリジン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix=settings.API_V1_STR)
app.include_router(recipes.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(text_to_sql.router, prefix=settings.API_V1_STR)


