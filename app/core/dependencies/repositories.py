from typing import Annotated
from fastapi import Depends
from supabase import Client, create_client
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.domain.auth.auth_repository import AuthRepository
from app.repository.auth.auth_postgres_repository import AuthPostgresRepository
from app.domain.practice.practice_repository import PracticeRepository
from app.repository.practicce.practice_supabase_repository import PracticeSupabaseRepository

def get_supabase_client():
    """Supabaseクライアントを生成する依存性"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_english_repository(client:Annotated[Client,Depends(get_supabase_client)]) -> PracticeRepository:
    """EnglishRepositoryのインスタンスを提供する依存性"""
    return PracticeSupabaseRepository(client)

def get_auth_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthRepository:
    """AuthRepositoryのインスタンスを提供する依存性"""
    # Supabaseから新しいPostgreSQLリポジトリに変更
    return AuthPostgresRepository(db)