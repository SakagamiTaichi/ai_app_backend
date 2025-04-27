# init_db.py
import asyncio
from app.core.database import engine, Base

async def init_db():
    async with engine.begin() as conn:
        # テーブルを削除して再作成する場合（開発時のみ）
        # await conn.run_sync(Base.metadata.drop_all)
        
        # テーブルを作成
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())