from typing import Annotated
from fastapi import Depends
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domain.auth.auth_repository import AuthRepository
from app.domain.email.emai_repository import EmailRepository
from app.domain.practice.practice_api_repotiroy import PracticeApiRepository
from app.domain.quiz.quize_repostiroy import QuizRepository
from app.domain.quizType.quiz_type_repository import QuizTypeRepository
from app.domain.recall.recall_card_repository import RecallCardrepository
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)
from app.domain.studyRecord.study_record_repository import StudyRecordRepository
from app.domain.userAnswer.study_ai_api_repository import StudyAiApiRepository
from app.domain.userAnswer.user_answer_repository import UserAnswerRepository
from app.repository.auth_postgres_repository import AuthPostgresRepository
from app.domain.practice.practice_repository import PracticeRepository
from app.repository.email_postgress_resend_repository import (
    EmailResendRepository,
)
from app.repository.practice_api_openai_repository import (
    PracticeApiOpenAiRepository,
)
from app.repository.practice_postgres_repository import (
    PracticePostgresRepository,
)
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from app.core.config import settings
from app.repository.quiz_postgres_repository import QuizPostgresRepository
from app.repository.quiz_type_postgres_repository import QuizTypePostgresRepository
from app.repository.recall_card_postgres_repository import RecallCardPostgresRepository
from app.repository.review_schedule_postgres_repository import (
    ReviewSchedulePostgresRepository,
)
from app.repository.study_ai_api_openai_repository import StudyAIAPIOpenAIRepository
from app.repository.study_record_postgres_repository import (
    StudyRecordPostgresRepository,
)
from app.repository.user_answer_postgres_repository import UserAnswerPostgresRepository


def get_chat_prompt_template() -> BaseChatModel:
    """ChatPromptTemplateのインスタンスを提供する依存性"""
    return ChatOpenAI(model=settings.OPENAI_MODEL, temperature=settings.TEMPERATURE)


def get_english_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticeRepository:
    """PracticeRepositoryのインスタンスを提供する依存性"""
    # PostgreSQLリポジトリに変更
    return PracticePostgresRepository(db)


def get_english_recall_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RecallCardrepository:
    """PracticeRepositoryのインスタンスを提供する依存性"""
    # PostgreSQLリポジトリに変更
    return RecallCardPostgresRepository(db)


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


def get_mail_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EmailRepository:
    """メール送信のためのAuthRepositoryのインスタンスを提供する依存性"""
    return EmailResendRepository()


def get_quiz_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuizRepository:
    """QuizRepositoryのインスタンスを提供する依存性"""
    return QuizPostgresRepository(db)


def get_quiz_type_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuizTypeRepository:
    """QuizTypeRepositoryのインスタンスを提供する依存性"""
    return QuizTypePostgresRepository(db)


def get_study_record_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StudyRecordRepository:
    """StudyRecordRepositoryのインスタンスを提供する依存性"""
    return StudyRecordPostgresRepository(db)


def get_review_schedule_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReviewScheduleRepository:
    """ReviewScheduleRepositoryのインスタンスを提供する依存性"""
    return ReviewSchedulePostgresRepository(db)


def get_user_answer_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserAnswerRepository:
    """RecallCardrepositoryのインスタンスを提供する依存性"""
    return UserAnswerPostgresRepository(db)


def get_study_ai_api_repository(
    llm: Annotated[BaseChatModel, Depends(get_chat_prompt_template)],
) -> StudyAiApiRepository:
    """StudyAiApiRepositoryのインスタンスを提供する依存性"""
    return StudyAIAPIOpenAIRepository(llm)
