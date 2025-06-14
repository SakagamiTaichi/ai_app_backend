# init_db.py
import asyncio
from app.core.database import engine, Base

# モデルをインポートすることで、Base.metadataに登録される
from app.schema.auth.models import UserModel  # type: ignore
from app.schema.practice.models import (
    ConversationModel,  # type: ignore
    MessageModel,  # type: ignore
    ConversationTestScoreModel,  # type: ignore
    MessageTestScoreModel,  # type: ignore
    LearningHistoryModel,  # type: ignore
)
from app.schema.recall.models import RecallCardModel  # type: ignore


async def init_db():
    async with engine.begin() as conn:
        # テーブルを削除して再作成する場合（開発時のみ）
        # await conn.run_sync(Base.metadata.drop_all)
        # テーブルを作成
        await conn.run_sync(Base.metadata.create_all)

    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
