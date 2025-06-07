import pytest
from datetime import datetime
from uuid import uuid4

from app.domain.practice.test_result_entity import (
    TestResultEntity,
    MessageScore,
    TestConstants,
)
from app.core.app_exception import BadRequestError


class TestMessageScore:
    """MessageScoreクラスのテストケース"""

    def test_init_valid_message_score(self):
        """正常なMessageScoreインスタンスの作成をテスト"""
        score = MessageScore(
            message_order=1,
            score=85.5,
            is_correct=True,
            user_answer="Hello world",
            correct_answer="Hello world"
        )
        
        assert score.message_order == 1
        assert score.score == 85.5
        assert score.is_correct is True
        assert score.user_answer == "Hello world"

    def test_init_invalid_message_order(self):
        """不正なmessage_orderでの作成時のバリデーションエラーをテスト"""
        with pytest.raises(ValueError):
            MessageScore(
                message_order=0,  # 1未満は無効
                score=85.5,
                is_correct=True,
                user_answer="Hello",
                correct_answer="Hello"
            )

    def test_init_invalid_score_range(self):
        """不正なスコア範囲での作成時のバリデーションエラーをテスト"""
        with pytest.raises(ValueError):
            MessageScore(
                message_order=1,
                score=101,  # 100超過は無効
                is_correct=True,
                user_answer="Hello",
                correct_answer="Hello"
            )
        
        with pytest.raises(ValueError):
            MessageScore(
                message_order=1,
                score=-1,  # 0未満は無効
                is_correct=True,
                user_answer="Hello",
                correct_answer="Hello"
            )

    def test_tokenize_basic_text(self):
        """基本的なテキストのトークン化をテスト"""
        text = "Hello, world! How are you?"
        tokens = MessageScore.tokenize(text)
        expected = ["Hello", ",", "world", "!", "How", "are", "you", "?"]
        assert tokens == expected

    def test_tokenize_with_contractions(self):
        """短縮形を含むテキストのトークン化をテスト"""
        text = "I'm happy, you're great!"
        tokens = MessageScore.tokenize(text)
        expected = ["I'm", "happy", ",", "you're", "great", "!"]
        assert tokens == expected

    def test_tokenize_empty_string(self):
        """空文字列のトークン化をテスト"""
        tokens = MessageScore.tokenize("")
        assert tokens == []

    def test_tokenize_whitespace_only(self):
        """空白のみの文字列のトークン化をテスト"""
        tokens = MessageScore.tokenize("   ")
        assert tokens == []

    def test_calculate_similarity_identical(self):
        """同一文字列の類似度計算をテスト"""
        similarity = MessageScore.calculate_similarity("Hello", "Hello")
        assert similarity == 100.0

    def test_calculate_similarity_completely_different(self):
        """完全に異なる文字列の類似度計算をテスト"""
        similarity = MessageScore.calculate_similarity("Hello", "World")
        assert 0 <= similarity <= 100

    def test_calculate_similarity_partial_match(self):
        """部分的に一致する文字列の類似度計算をテスト"""
        similarity = MessageScore.calculate_similarity("Hello world", "Hello earth")
        assert 0 < similarity < 100

    def test_get_matcher(self):
        """SequenceMatcherの取得をテスト"""
        matcher = MessageScore.get_matcher("Hello", "Hello")
        assert matcher.ratio() == 1.0

    def test_get_diff_blocks(self):
        """差分ブロックの取得をテスト"""
        user_tokens = ["Hello", "world"]
        correct_tokens = ["Hello", "earth"]
        blocks = MessageScore.get_diff_blocks(user_tokens, correct_tokens)
        assert isinstance(blocks, list)
        assert len(blocks) > 0

    def test_computed_field_tokenized_user_answer(self):
        """ユーザー回答のトークン化computed fieldをテスト"""
        score = MessageScore(
            message_order=1,
            score=85.5,
            is_correct=True,
            user_answer="Hello, world!",
            correct_answer="Hello world"
        )
        
        tokens = score.get_tokenized_user_answer
        expected = ["Hello", ",", "world", "!"]
        assert tokens == expected

    def test_factory_method_perfect_match(self):
        """完全一致時のfactoryメソッドをテスト"""
        score = MessageScore.factory(
            message_order=1,
            user_answer="Hello world",
            correct_answer="Hello world"
        )
        
        assert score.message_order == 1
        assert score.score == 100.0
        assert score.is_correct is True
        assert score.user_answer == "Hello world"

    def test_factory_method_below_threshold(self):
        """閾値以下のスコア時のfactoryメソッドをテスト"""
        score = MessageScore.factory(
            message_order=2,
            user_answer="Wrong answer",
            correct_answer="Correct answer"
        )
        
        assert score.message_order == 2
        assert score.score < TestConstants.CORRECT_THRESHOLD
        assert score.is_correct is False


class TestTestResultEntity:
    """TestResultEntityクラスのテストケース"""

    def test_init_valid_test_result(self):
        """正常なTestResultEntityインスタンスの作成をテスト"""
        conversation_id = uuid4()
        message_scores = [
            MessageScore(
                message_order=1,
                score=90.0,
                is_correct=True,
                user_answer="Hello",
                correct_answer="Hello"
            )
        ]
        
        result = TestResultEntity(
            conversation_id=conversation_id,
            test_number=1,
            message_scores=message_scores
        )
        
        assert result.conversation_id == conversation_id
        assert result.test_number == 1
        assert len(result.message_scores) == 1
        assert isinstance(result.created_at, datetime)

    def test_init_with_defaults(self):
        """デフォルト値でのTestResultEntityインスタンス作成をテスト"""
        conversation_id = uuid4()
        
        result = TestResultEntity(
            conversation_id=conversation_id,
            test_number=1,
            message_scores=[
                MessageScore(
                    message_order=1,
                    score=90.0,
                    is_correct=True,
                    user_answer="Hello",
                    correct_answer="Hello"
                )
            ]
        )
        
        assert isinstance(result.created_at, datetime)
        assert len(result.message_scores) == 1

    def test_validate_empty_message_scores(self):
        """空のメッセージスコアでのバリデーションエラーをテスト"""
        conversation_id = uuid4()
        
        with pytest.raises(BadRequestError):
            TestResultEntity(
                conversation_id=conversation_id,
                test_number=1,
                message_scores=[]
            )

    def test_overall_score_single_message(self):
        """単一メッセージの全体スコア計算をテスト"""
        conversation_id = uuid4()
        message_scores = [
            MessageScore(
                message_order=1,
                score=85.5,
                is_correct=True,
                user_answer="Hello",
                correct_answer="Hello"
            )
        ]
        
        result = TestResultEntity(
            conversation_id=conversation_id,
            test_number=1,
            message_scores=message_scores
        )
        
        assert result.overall_score == 86  # round(85.5)

    def test_overall_score_multiple_messages(self):
        """複数メッセージの全体スコア計算をテスト"""
        conversation_id = uuid4()
        message_scores = [
            MessageScore(
                message_order=1,
                score=80.0,
                is_correct=False,
                user_answer="Hello",
                correct_answer="Hi"
            ),
            MessageScore(
                message_order=2,
                score=90.0,
                is_correct=True,
                user_answer="Good",
                correct_answer="Good"
            ),
            MessageScore(
                message_order=3,
                score=85.0,
                is_correct=True,
                user_answer="Yes",
                correct_answer="Yes"
            )
        ]
        
        result = TestResultEntity(
            conversation_id=conversation_id,
            test_number=1,
            message_scores=message_scores
        )
        
        expected_score = round((80.0 + 90.0 + 85.0) / 3)  # 85
        assert result.overall_score == expected_score

    def test_overall_score_empty_messages(self):
        """メッセージなしの場合の全体スコア計算をテスト"""
        # この場合はバリデーションで弾かれるが、万が一のため
        conversation_id = uuid4()
        
        # Pydanticのバリデーションを回避して直接インスタンス作成
        result = TestResultEntity.model_construct(
            conversation_id=conversation_id,
            test_number=1,
            message_scores=[],
            created_at=datetime.now()
        )
        
        assert result.overall_score == 0

    def test_is_passing_above_threshold(self):
        """合格閾値以上での合格判定をテスト"""
        conversation_id = uuid4()
        message_scores = [
            MessageScore(
                message_order=1,
                score=85.0,
                is_correct=True,
                user_answer="Hello",
                correct_answer="Hello"
            )
        ]
        
        result = TestResultEntity(
            conversation_id=conversation_id,
            test_number=1,
            message_scores=message_scores
        )
        
        assert result.is_passing is True

    def test_is_passing_below_threshold(self):
        """合格閾値以下での不合格判定をテスト"""
        conversation_id = uuid4()
        message_scores = [
            MessageScore(
                message_order=1,
                score=75.0,
                is_correct=False,
                user_answer="Hello",
                correct_answer="Hi"
            )
        ]
        
        result = TestResultEntity(
            conversation_id=conversation_id,
            test_number=1,
            message_scores=message_scores
        )
        
        assert result.is_passing is False

    def test_is_passing_exactly_threshold(self):
        """合格閾値ちょうどでの合格判定をテスト"""
        conversation_id = uuid4()
        message_scores = [
            MessageScore(
                message_order=1,
                score=80.0,
                is_correct=False,
                user_answer="Hello",
                correct_answer="Hi"
            )
        ]
        
        result = TestResultEntity(
            conversation_id=conversation_id,
            test_number=1,
            message_scores=message_scores
        )
        
        assert result.is_passing is True

    def test_factory_method_valid_answers(self):
        """正常な回答リストでのfactoryメソッドをテスト"""
        conversation_id = uuid4()
        answers = [
            {
                "message_order": "1",
                "user_answer": "Hello world",
                "correct_answer": "Hello world"
            },
            {
                "message_order": "2",
                "user_answer": "Good morning",
                "correct_answer": "Good morning"
            }
        ]
        
        result = TestResultEntity.factory(
            conversation_id=conversation_id,
            test_number=1,
            answers=answers
        )
        
        assert result.conversation_id == conversation_id
        assert result.test_number == 1
        assert len(result.message_scores) == 2
        assert result.message_scores[0].message_order == 1
        assert result.message_scores[1].message_order == 2
        assert result.overall_score == 100  # 完全一致

    def test_factory_method_mixed_scores(self):
        """様々なスコアの回答リストでのfactoryメソッドをテスト"""
        conversation_id = uuid4()
        answers = [
            {
                "message_order": "1",
                "user_answer": "Hello world",
                "correct_answer": "Hello world"  # 完全一致
            },
            {
                "message_order": "2",
                "user_answer": "Wrong answer",
                "correct_answer": "Correct answer"  # 部分一致
            }
        ]
        
        result = TestResultEntity.factory(
            conversation_id=conversation_id,
            test_number=1,
            answers=answers
        )
        
        assert len(result.message_scores) == 2
        assert result.message_scores[0].score == 100.0
        assert result.message_scores[0].is_correct is True
        assert result.message_scores[1].score < 100.0


class TestTestConstants:
    """TestConstantsクラスのテストケース"""

    def test_constants_values(self):
        """定数値の確認をテスト"""
        assert TestConstants.CORRECT_THRESHOLD == 90
        assert TestConstants.PASSING_THRESHOLD == 80

    def test_constants_immutability(self):
        """定数の不変性をテスト（クラス属性として定義されていることを確認）"""
        assert hasattr(TestConstants, 'CORRECT_THRESHOLD')
        assert hasattr(TestConstants, 'PASSING_THRESHOLD')
        assert isinstance(TestConstants.CORRECT_THRESHOLD, int)
        assert isinstance(TestConstants.PASSING_THRESHOLD, int)


class TestIntegration:
    """統合テストケース"""

    def test_end_to_end_test_result_creation(self):
        """エンドツーエンドのテスト結果作成をテスト"""
        conversation_id = uuid4()
        answers = [
            {
                "message_order": "1",
                "user_answer": "I am fine, thank you.",
                "correct_answer": "I am fine, thank you."
            },
            {
                "message_order": "2",
                "user_answer": "Good morning!",
                "correct_answer": "Good morning!"
            },
            {
                "message_order": "3",
                "user_answer": "See you later",
                "correct_answer": "See you tomorrow"
            }
        ]
        
        result = TestResultEntity.factory(
            conversation_id=conversation_id,
            test_number=1,
            answers=answers
        )
        
        # 結果の検証
        assert len(result.message_scores) == 3
        assert result.message_scores[0].is_correct is True  # 完全一致
        assert result.message_scores[1].is_correct is True  # 完全一致
        assert result.message_scores[2].is_correct is False  # 部分一致のみ
        
        # 全体スコアが適切に計算されることを確認
        assert 0 <= result.overall_score <= 100
        
        # 合格判定が適切に行われることを確認
        if result.overall_score >= TestConstants.PASSING_THRESHOLD:
            assert result.is_passing is True
        else:
            assert result.is_passing is False

    def test_edge_case_single_character_answers(self):
        """単一文字回答のエッジケースをテスト"""
        conversation_id = uuid4()
        answers = [
            {
                "message_order": "1",
                "user_answer": "A",
                "correct_answer": "A"
            },
            {
                "message_order": "2",
                "user_answer": "B",
                "correct_answer": "C"
            }
        ]
        
        result = TestResultEntity.factory(
            conversation_id=conversation_id,
            test_number=1,
            answers=answers
        )
        
        assert len(result.message_scores) == 2
        assert result.message_scores[0].score == 100.0
        assert result.message_scores[1].score == 0.0

    def test_edge_case_empty_answers(self):
        """空の回答のエッジケースをテスト"""
        conversation_id = uuid4()
        answers = [
            {
                "message_order": "1",
                "user_answer": "",
                "correct_answer": "Hello"
            }
        ]
        
        result = TestResultEntity.factory(
            conversation_id=conversation_id,
            test_number=1,
            answers=answers
        )
        
        assert len(result.message_scores) == 1
        assert result.message_scores[0].score == 0.0
        assert result.message_scores[0].is_correct is False