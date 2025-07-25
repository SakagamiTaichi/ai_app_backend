from datetime import datetime
from uuid import UUID
from typing import List, Dict
from pydantic import BaseModel, Field, computed_field, field_validator
import re
import difflib

from app.core.app_exception import BadRequestError


class TestConstants:
    """テストの定数"""

    CORRECT_THRESHOLD: int = 90  # 一つのメッセージが正解と判定される閾値
    PASSING_THRESHOLD: int = 80  # テスト全体の合格閾値


class MessageScoreValueObject(BaseModel):
    """メッセージごとのテストスコアを表すバリューオブジェクト"""

    message_order: int = Field(ge=1, description="メッセージの順番（1以上）")
    score: float = Field(ge=0, le=100, description="スコア（0〜100）")
    isCorrect: bool
    userAnswer: str
    correctAnswer: str

    @staticmethod
    def tokenize(text: str) -> List[str]:
        # 前処理を追加
        text = text.strip()
        return re.findall(r"\b[\w\']+\b|[.,;!?]|\S", text)

    @staticmethod
    def get_matcher(user_answer: str, correct_answer: str):
        return difflib.SequenceMatcher(None, user_answer, correct_answer)

    @staticmethod
    def calculate_similarity(user_answer: str, correct_answer: str) -> float:
        """ユーザーの回答と正解の類似度を計算する"""
        matcher = MessageScoreValueObject.get_matcher(user_answer, correct_answer)
        return round(matcher.ratio() * 100)

    @staticmethod
    def get_diff_blocks(
        user_answer: List[str], correct_answer: List[str]
    ) -> List[tuple]:
        """ユーザーの回答と正解の差分を取得する"""
        matcher = difflib.SequenceMatcher(None, user_answer, correct_answer)
        return matcher.get_opcodes()

    @computed_field
    @property
    def get_tokenized_user_answer(self) -> List[str]:
        """ユーザーの回答をトークン化して返す"""
        return self.tokenize(self.userAnswer)

    @computed_field
    @property
    def get_tokenized_correct_answer(self) -> List[str]:
        """正解の回答をトークン化して返す"""
        return self.tokenize(self.correctAnswer)

    @classmethod
    def factory(
        cls, message_order: int, user_answer: str, correct_answer: str
    ) -> "MessageScoreValueObject":
        """メッセージスコアを計算して作成する"""
        score = cls.calculate_similarity(user_answer, correct_answer)
        return cls(
            message_order=message_order,
            score=score,
            isCorrect=score >= TestConstants.CORRECT_THRESHOLD,
            userAnswer=user_answer,
            correctAnswer=correct_answer,
        )


class TestResultEntity(BaseModel):
    """テスト結果を表すエンティティ（集約ルート）"""

    conversation_id: UUID
    test_number: int
    message_scores: List[MessageScoreValueObject] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("message_scores", mode="before")
    @classmethod
    def validate_message_scores(cls, value: List[MessageScoreValueObject]):
        if not value:
            raise BadRequestError(detail="メッセージスコアは1つ以上必要です")
        return value

    @computed_field
    @property
    def overall_score(self) -> int:
        """全体のスコアを計算する"""
        if not self.message_scores:
            return 0
        # 整数に変換
        return round(
            sum(score.score for score in self.message_scores) / len(self.message_scores)
        )

    @computed_field
    @property
    def is_passing(self) -> bool:
        """合格判定（80%以上で合格）"""
        return self.overall_score >= TestConstants.PASSING_THRESHOLD

    @classmethod
    def factory(
        cls, conversation_id: UUID, test_number: int, answers: List[Dict[str, str]]
    ) -> "TestResultEntity":
        """ユーザーの回答リストからテスト結果を作成する"""
        result = cls(conversation_id=conversation_id, test_number=test_number)

        for answer in answers:
            score = MessageScoreValueObject.factory(
                message_order=int(answer["message_order"]),
                user_answer=answer["user_answer"],
                correct_answer=answer["correct_answer"],
            )
            result.message_scores.append(score)

        return result
