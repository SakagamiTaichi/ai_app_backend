import datetime
from uuid import UUID
from app.domain.quiz.quize_repostiroy import QuizRepository

from app.domain.reviewSchedule.review_schedule_domain_service import (
    ReviewScheduleDomainService,
)
from app.domain.reviewSchedule.review_schedule_repository import (
    ReviewScheduleRepository,
)
from app.domain.studyRecord.study_record_repository import StudyRecordRepository
from app.domain.userAnswer.user_answer_domain_service import UserAnswerDomainService
from app.domain.userAnswer.user_answer_repository import UserAnswerRepository
from app.endpoint.home.home_model import HomeResponse


class HomeService:
    def __init__(
        self,
        reviewScheduleRepository: ReviewScheduleRepository,
        quizRepository: QuizRepository,
        studyRecordRepository: StudyRecordRepository,
        userAnswerRepository: UserAnswerRepository,
    ):
        self.reviewScheduleRepository = reviewScheduleRepository
        self.quizRepository = quizRepository
        self.studyRecordRepository = studyRecordRepository
        self.userAnswerRepository = userAnswerRepository

    async def get_home(self, user_id: UUID) -> HomeResponse:
        """ホーム画面の情報を取得する。"""

        nowTime = datetime.datetime.now()
        # 朝昼夜に応じてメッセージを変える
        if nowTime.hour < 12:
            greeting = "おはようございます！"
        elif nowTime.hour < 18:
            greeting = "こんにちは！"
        else:
            greeting = "こんばんは！"

        # 連続学習日数を取得する
        studyRecord = await self.studyRecordRepository.getAllByUserId(user_id)

        # ユーザーの平均得点を取得する。
        userAnswerDomainService = UserAnswerDomainService(
            quizRepository=self.quizRepository,
            userAnswerRepository=self.userAnswerRepository,
        )

        # TODO 2回もデータベースから取得している。パフォーマンスの改善の余地あり。
        average_score = await userAnswerDomainService.get_average_score(user_id)
        all_quiz_count = await userAnswerDomainService.get_not_answered_quiz_count(
            user_id
        )

        # 復習期限が過ぎたレビューを取得する
        reviewScheduleDomainService = ReviewScheduleDomainService(
            reviewShceduleRepository=self.reviewScheduleRepository
        )

        pending_review_count = (
            await reviewScheduleDomainService.get_after_deadline_count(user_id)
        )

        return HomeResponse(
            message=greeting,
            continuous_learning_days=studyRecord.getContinuousLearningDays(),
            pending_review_count=pending_review_count,
            all_quiz_count=all_quiz_count,
            average_score=average_score,
        )
