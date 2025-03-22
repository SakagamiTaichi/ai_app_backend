from fastapi import FastAPI
from app.api.v1.endpoints import  auth, english, health_check
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from app.core.config import settings
from fastapi.middleware.trustedhost import TrustedHostMiddleware

if settings.ENVIRONMENT == "production":
    # 本番環境用の設定
        app = FastAPI(
        title="EIGOAT API",
        description="",
        version="1.0.0",
        docs_url=None,  # 本番環境ではSwaggerUIを無効化
        redoc_url=None  # 本番環境ではRedocを無効化
    )
else:
    # 開発環境以外の設定
    # HTTPSリダイレクトを強制（本番環境用）
    # FastAPIインスタンスの作成
    app = FastAPI(
    title="EIGOAT API",
    description="",
    version="1.0.0")
    app.add_middleware(HTTPSRedirectMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hostヘッダインジェクション対策
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "ai-app-backend-zr75.onrender.com",  # 本番環境
        "localhost:8000"                     # 開発環境
    ]
)

app.include_router(health_check.router, prefix=settings.API_V1_STR)
app.include_router(english.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)  # 認証エンドポイントを追加


