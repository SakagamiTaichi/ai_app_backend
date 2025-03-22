from typing import Annotated
from fastapi import Depends
from supabase import Client, create_client

from app.core.config import settings
from app.features.auth.domain.auth_repository import AuthRepository
from app.features.auth.repository.auth_supabase_repository import AuthSupabaseRepository
from app.features.practice.domain.practice_repository import PracticeRepository
from app.features.practice.repository.practice_supabase_repository import PracticeSupabaseRepository

def get_supabase_client():
    """Supabaseクライアントを生成する依存性"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_english_repository(client:Annotated[Client,Depends(get_supabase_client)]) -> PracticeRepository:
    """EnglishRepositoryのインスタンスを提供する依存性"""
    return PracticeSupabaseRepository(client)

def get_auth_repository(client: Annotated[Client, Depends(get_supabase_client)]) -> AuthRepository:
    """AuthRepositoryのインスタンスを提供する依存性"""
    return AuthSupabaseRepository(client)