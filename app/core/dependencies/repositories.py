from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domain.auth.auth_repository import AuthRepository
from app.repository.auth.auth_postgres_repository import AuthPostgresRepository
from app.domain.practice.practice_repository import PracticeRepository
from app.repository.practicce.practice_postgres_repository import PracticePostgresRepository


def get_english_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> PracticeRepository:
    """PracticeRepositoryのインスタンスを提供する依存性"""
    # PostgreSQLリポジトリに変更
    return PracticePostgresRepository(db)

def get_auth_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthRepository:
    """AuthRepositoryのインスタンスを提供する依存性"""
    # Supabaseから新しいPostgreSQLリポジトリに変更
    return AuthPostgresRepository(db)