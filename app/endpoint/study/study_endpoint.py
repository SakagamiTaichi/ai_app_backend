# ヘルスチェックAPI

from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer

from app.core.dependencies.repositories import (
    get_auth_repository,
    get_mail_repository,
    get_quiz_repository,
    get_quiz_type_repository,
    get_review_schedule_repository,
    get_study_ai_api_repository,
    get_user_answer_repository,
)
from app.domain.auth.auth_repository import AuthRepository
from app.domain.email.emai_repository import EmailRepository
from app.domain.quiz.quize_repostiroy import QuizRepository
from app.domain.quizType.quiz_type_repository import QuizTypeRepository
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)
from app.domain.userAnswer.study_ai_api_repository import StudyAiApiRepository
from app.domain.userAnswer.user_answer_repository import UserAnswerRepository
from app.endpoint.study.study_model import (
    QuizAnswerRequest,
    QuizAnswerResponse,
    QuizStudyRecordResponse,
    QuizStudyRecordsResponse,
    QuizTypesResponse,
    QuizResponse,
)
from app.services.auth_service import AuthService
from app.services.study_service import StudyService

router = APIRouter(prefix="/study", tags=["study"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/token")


# サービスのインスタンス作成に依存性注入を使用
def get_service(
    quizRepository: Annotated[QuizRepository, Depends(get_quiz_repository)],
    userAnswerRepository: Annotated[
        UserAnswerRepository, Depends(get_user_answer_repository)
    ],
    quizTypeRepository: Annotated[
        QuizTypeRepository, Depends(get_quiz_type_repository)
    ],
    reviewScheduleRepository: Annotated[
        ReviewScheduleRepository, Depends(get_review_schedule_repository)
    ],
    aiAPIRepository: Annotated[
        StudyAiApiRepository, Depends(get_study_ai_api_repository)
    ],
) -> StudyService:
    return StudyService(
        quizRepository=quizRepository,
        userAnswerRepository=userAnswerRepository,
        quiZTypeRepository=quizTypeRepository,
        reviewScheduleRepository=reviewScheduleRepository,
        aiAPIRepository=aiAPIRepository,
    )


def get_auth_service(
    repository: Annotated[AuthRepository, Depends(get_auth_repository)],
    mailRepository: Annotated[EmailRepository, Depends(get_mail_repository)],
) -> AuthService:
    return AuthService(repository, mailRepository)


@router.get("/quiz_type")
async def get_quiz_types(
    study_service: Annotated[StudyService, Depends(get_service)],
) -> QuizTypesResponse:
    """クイズの種類を取得するエンドポイント"""
    return await study_service.get_quiz_type()


@router.get("/quiz")
async def get_quizzes(
    token: Annotated[str, Depends(oauth2_scheme)],
    study_service: Annotated[StudyService, Depends(get_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    quiz_type_id: Annotated[Optional[UUID], Query(description="クイズの種類ID")] = None,
    question_type: Annotated[Optional[str], Query(description="復習・新規")] = None,
) -> QuizResponse:
    """クイズを取得するエンドポイント"""
    current_user = await auth_service.get_current_user(token)
    return await study_service.get_quizzes(current_user.id, quiz_type_id, question_type)


@router.get("/records")
async def get_study_records(
    token: Annotated[str, Depends(oauth2_scheme)],
    study_service: Annotated[StudyService, Depends(get_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> QuizStudyRecordsResponse:
    """クイズの学習履歴をまとめて取得するエンドポイント"""
    current_user = await auth_service.get_current_user(token)

    return await study_service.get_study_records(current_user.id)


@router.get("/record/{user_answer_id}")
async def get_study_record(
    token: Annotated[str, Depends(oauth2_scheme)],
    study_service: Annotated[StudyService, Depends(get_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_answer_id: UUID,
) -> QuizStudyRecordResponse:
    """特定のユーザーの回答を取得するエンドポイント"""
    current_user = await auth_service.get_current_user(token)

    return await study_service.get_study_record(current_user.id, user_answer_id)


@router.post("/quiz-answer")
async def create_quiz_answer(
    request: QuizAnswerRequest,
    token: Annotated[str, Depends(oauth2_scheme)],
    study_service: Annotated[StudyService, Depends(get_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> QuizAnswerResponse:
    """ユーザーの回答を添削するエンドポイント"""
    current_user = await auth_service.get_current_user(token)

    return await study_service.create_quiz_answer(request, current_user.id)
