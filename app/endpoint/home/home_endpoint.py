# ヘルスチェックAPI

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.dependencies.repositories import (
    get_auth_repository,
    get_mail_repository,
    get_quiz_repository,
    get_review_schedule_repository,
    get_study_record_repository,
    get_user_answer_repository,
)
from app.domain.auth.auth_repository import AuthRepository
from app.domain.email.emai_repository import EmailRepository
from app.domain.quiz.quize_repostiroy import QuizRepository
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)
from app.domain.studyRecord.study_record_repository import StudyRecordRepository
from app.domain.userAnswer.user_answer_repository import UserAnswerRepository
from app.endpoint.home.home_model import HomeResponse
from app.services.auth_service import AuthService
from app.services.home_service import HomeService

router = APIRouter(prefix="/home", tags=["home"])

# OAuth2のパスワードベアラースキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/token")


# サービスのインスタンス作成に依存性注入を使用
def get_service(
    reviewScheduleRepository: Annotated[
        ReviewScheduleRepository, Depends(get_review_schedule_repository)
    ],
    quizRepository: Annotated[QuizRepository, Depends(get_quiz_repository)],
    studyRecordRepository: Annotated[
        StudyRecordRepository, Depends(get_study_record_repository)
    ],
    userAnswerRepository: Annotated[
        UserAnswerRepository, Depends(get_user_answer_repository)
    ],
) -> HomeService:
    return HomeService(
        reviewScheduleRepository=reviewScheduleRepository,
        quizRepository=quizRepository,
        studyRecordRepository=studyRecordRepository,
        userAnswerRepository=userAnswerRepository,
    )


def get_auth_service(
    repository: Annotated[AuthRepository, Depends(get_auth_repository)],
    mailRepository: Annotated[EmailRepository, Depends(get_mail_repository)],
) -> AuthService:
    return AuthService(repository, mailRepository)


@router.get("/", response_model=HomeResponse)
async def home(
    token: Annotated[str, Depends(oauth2_scheme)],
    home_service: Annotated[HomeService, Depends(get_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> HomeResponse:
    """ホーム画面の情報を取得する"""
    try:
        # 現在のユーザー情報を取得
        current_user = await auth_service.get_current_user(token)
        # ユーザーIDに基づいてホーム情報を取得
        return await home_service.get_home(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
