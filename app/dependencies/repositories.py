from typing import Annotated
from fastapi import Depends
from supabase import Client, create_client

from app.core.config import settings
from app.repositories.auth_repository import AuthRepository
from app.repositories.auth_supabase_repository import AuthSupabaseRepository
from app.repositories.english_repository import EnglishRepository
from app.repositories.english_supabase_repository import EnglishSupabaseRepository
from app.services.auth_service import AuthService

def get_supabase_client():
    """Supabaseクライアントを生成する依存性"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_english_repository(client:Annotated[Client,Depends(get_supabase_client)]) -> EnglishRepository:
    """EnglishRepositoryのインスタンスを提供する依存性"""
    return EnglishSupabaseRepository(client)

def get_auth_repository(client: Annotated[Client, Depends(get_supabase_client)]) -> AuthRepository:
    """AuthRepositoryのインスタンスを提供する依存性"""
    return AuthSupabaseRepository(client)

def get_auth_service(repo: Annotated[AuthRepository, Depends(get_auth_repository)]) -> AuthService:
    """AuthServiceのインスタンスを提供する依存性"""
    return AuthService(repo)