# FastAPIアプリケーションでSQLAlchemyを使用して非同期データベース接続を設定するためのデータベース設定ファイル
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 非同期用のデータベースエンジンを作成
engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)

# 非同期セッションを生成するためのファクトリーを作成
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# SQLAlchemyのORMモデルを定義するための基底クラス
Base = declarative_base()

# FastAPIのルートハンドラーに注入されるデータベースセッションを提供
async def get_db():
    async with async_session() as session:
        yield session