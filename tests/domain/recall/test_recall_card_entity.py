import datetime
from uuid import UUID
from app.domain.recall.reacall_card_entity import RecallCardConstants, RecallCardEntity


class TestRecallCardEntity:
    """RecallCardEntityクラスのテストケース"""

    def test_init_valid_recall_card(self):
        """正常なRecallCardEntityインスタンスの作成をテスト"""
        recall_card = RecallCardEntity(
            recallCardId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            question="What is the capital of France?",
            answer="Paris",
            correctPoint=10,
            reviewDeadline=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        assert recall_card.recallCardId == UUID("123e4567-e89b-12d3-a456-426614174000")
        assert recall_card.userId == UUID("123e4567-e89b-12d3-a456-426614174001")
        assert recall_card.question == "What is the capital of France?"
        assert recall_card.answer == "Paris"
        assert recall_card.correctPoint == 10
        assert recall_card.reviewDeadline == datetime.datetime(2023, 10, 1, 12, 0, 0)

    def test_update_correct_recall_card(self):
        """正答時のRecallCardEntityの更新をテスト"""
        recall_card = RecallCardEntity(
            recallCardId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            question="What is the capital of France?",
            answer="Paris",
            correctPoint=2,
            reviewDeadline=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        updated_card = recall_card.update_by_user_answer("Paris")
        assert updated_card.correctPoint == 3
        assert updated_card.reviewDeadline == datetime.datetime(
            2023, 10, 1, 12, 0, 0
        ) + datetime.timedelta(
            minutes=3**RecallCardConstants.REVIEW_DEADLINE_COEFFICIENT
        )

    def test_update_incorrect_recall_card(self):
        """不正解時のRecallCardEntityの更新をテスト"""
        recall_card = RecallCardEntity(
            recallCardId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            question="What is the capital of France?",
            answer="Paris",
            correctPoint=9,
            reviewDeadline=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        updated_card = recall_card.update_by_user_answer("London")
        assert (
            updated_card.correctPoint == 9 - RecallCardConstants.CORRECT_POINT_DECREMENT
        )
        assert updated_card.reviewDeadline == datetime.datetime(2023, 10, 1, 12, 0, 0)

    def test_update_with_negative_correct_point(self):
        """不正解時に正解ポイントが負数にならないことをテスト"""
        recall_card = RecallCardEntity(
            recallCardId=UUID("123e4567-e89b-12d3-a456-426614174000"),
            userId=UUID("123e4567-e89b-12d3-a456-426614174001"),
            question="What is the capital of France?",
            answer="Paris",
            correctPoint=0,
            reviewDeadline=datetime.datetime(2023, 10, 1, 12, 0, 0),
        )
        updated_card = recall_card.update_by_user_answer("London")
        assert updated_card.correctPoint == 0
        assert updated_card.reviewDeadline == datetime.datetime(2023, 10, 1, 12, 0, 0)
