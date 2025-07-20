import datetime
from uuid import UUID
from app.domain.reviewSchedule.review_schedule_entity import (
    ReviewScheduleEntity,
    RecallCardConstants,
)


class TestReviewScheduleEntity:
    """ReviewScheduleEntityクラスのテストケース"""

    def test_init_valid_review_schedule(self):
        """正常なReviewScheduleEntityインスタンスの作成をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        assert review_schedule.reviewScheduleId == UUID(
            "123e4567-e89b-12d3-a456-426614174000"
        )
        assert review_schedule.userId == UUID("123e4567-e89b-12d3-a456-426614174001")
        assert review_schedule.quizId == UUID("123e4567-e89b-12d3-a456-426614174002")
        assert review_schedule.reviewDeadLine == datetime.datetime(
            2023, 10, 1, 12, 0, 0
        )

    def test_update_with_empty_scores(self):
        """空のスコアリストでの更新をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        updated_schedule = review_schedule.update([])
        assert updated_schedule == review_schedule

    def test_update_with_high_score(self):
        """高得点スコアでの更新をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        updated_schedule = review_schedule.update([95])
        # 最新スコア係数: 3.0, 連続性係数: 1.0, 平均補正係数: 1.2
        multiplier = 3.0 * 1.0 * 1.2
        expected_date = (
            datetime.date.today() + RecallCardConstants.BASIC_ADD_DEADLINE * multiplier
        )
        assert updated_schedule.reviewDeadLine == expected_date

    def test_update_with_low_score(self):
        """低得点スコアでの更新をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        updated_schedule = review_schedule.update([30])
        # 最新スコア係数: 0.2, 連続性係数: 1.0, 平均補正係数: 0.6
        multiplier = 0.2 * 1.0 * 0.6
        expected_date = (
            datetime.date.today() + RecallCardConstants.BASIC_ADD_DEADLINE * multiplier
        )
        assert updated_schedule.reviewDeadLine == expected_date

    def test_update_with_consecutive_high_scores(self):
        """連続高得点での更新をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        # 4回連続高得点（80点以上）
        scores = [85, 88, 82, 90]
        updated_schedule = review_schedule.update(scores)
        # 最新スコア係数: 3.0, 連続性係数: 2.0, 平均補正係数: 1.2
        multiplier = 3.0 * 2.0 * 1.2
        expected_date = (
            datetime.date.today() + RecallCardConstants.BASIC_ADD_DEADLINE * multiplier
        )
        assert updated_schedule.reviewDeadLine == expected_date

    def test_update_with_consecutive_low_scores(self):
        """連続低得点での更新をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        # 3回連続低得点（50点未満）
        scores = [30, 40, 20]
        updated_schedule = review_schedule.update(scores)
        # 最新スコア係数: 0.2, 連続性係数: 0.5, 平均補正係数: 0.6
        multiplier = 0.2 * 0.5 * 0.6
        expected_date = (
            datetime.date.today() + RecallCardConstants.BASIC_ADD_DEADLINE * multiplier
        )
        assert updated_schedule.reviewDeadLine == expected_date

    def test_get_latest_score_multiplier(self):
        """最新スコア係数の取得をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )

        assert review_schedule._get_latest_score_multiplier(95) == 3.0
        assert review_schedule._get_latest_score_multiplier(85) == 2.0
        assert review_schedule._get_latest_score_multiplier(70) == 1.0
        assert review_schedule._get_latest_score_multiplier(50) == 0.4
        assert review_schedule._get_latest_score_multiplier(25) == 0.2

    def test_get_continuity_multiplier(self):
        """連続性係数の取得をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )

        # 単一スコアの場合
        assert review_schedule._get_continuity_multiplier([80]) == 1.0

        # 4回連続高得点
        assert review_schedule._get_continuity_multiplier([80, 85, 82, 90]) == 2.0

        # 3回連続高得点
        assert review_schedule._get_continuity_multiplier([70, 80, 85, 82]) == 1.5

        # 2回連続高得点
        assert review_schedule._get_continuity_multiplier([70, 80, 85]) == 1.2

        # 3回連続低得点
        assert review_schedule._get_continuity_multiplier([30, 40, 20]) == 0.5

        # 2回連続低得点
        assert review_schedule._get_continuity_multiplier([60, 40, 20]) == 0.7

        # 連続性がない場合
        assert review_schedule._get_continuity_multiplier([60, 70, 75]) == 1.0

    def test_get_average_correction_multiplier(self):
        """平均補正係数の取得をテスト"""
        review_schedule = ReviewScheduleEntity(
            reviewScheduleId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            quizId=UUID("123e4567-e89b-12d3-a456-426614174002"),
            reviewDeadLine=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )

        # 空リストの場合
        assert review_schedule._get_average_correction_multiplier([]) == 1.0

        # 平均80点以上
        assert review_schedule._get_average_correction_multiplier([80, 85, 90]) == 1.2

        # 平均60-79点
        assert review_schedule._get_average_correction_multiplier([60, 70, 75]) == 1.0

        # 平均40-59点
        assert review_schedule._get_average_correction_multiplier([40, 50, 55]) == 0.8

        # 平均40点未満
        assert review_schedule._get_average_correction_multiplier([20, 30, 35]) == 0.6
