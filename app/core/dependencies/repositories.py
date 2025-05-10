from typing import Annotated
from fastapi import Depends
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domain.auth.auth_repository import AuthRepository
from app.domain.practice.practice_api_repotiroy import PracticeApiRepository
from app.repository.auth.auth_postgres_repository import AuthPostgresRepository
from app.domain.practice.practice_repository import PracticeRepository
from app.repository.practicce.practice_api_openai_repository import (
    PracticeApiOpenAiRepository,
)
from app.repository.practicce.practice_postgres_repository import (
    PracticePostgresRepository,
)
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from app.core.config import settings


def get_chat_prompt_template() -> BaseChatModel:
    """ChatPromptTemplateのインスタンスを提供する依存性"""
    return ChatOpenAI(model=settings.OPENAI_MODEL, temperature=settings.TEMPERATURE)


def get_english_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticeRepository:
    """PracticeRepositoryのインスタンスを提供する依存性"""
    # PostgreSQLリポジトリに変更
    return PracticePostgresRepository(db)


def get_english_api_repository(
    llm: Annotated[BaseChatModel, Depends(get_chat_prompt_template)],
) -> PracticeApiRepository:
    """PracticeApiRepositoryのインスタンスを提供する依存性"""
    # PostgreSQLリポジトリに変更
    return PracticeApiOpenAiRepository(llm)


def get_auth_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthRepository:
    """AuthRepositoryのインスタンスを提供する依存性"""
    # Supabaseから新しいPostgreSQLリポジトリに変更
    return AuthPostgresRepository(db)
