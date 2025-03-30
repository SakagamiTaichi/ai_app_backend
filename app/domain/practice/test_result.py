from datetime import datetime
from uuid import UUID
from typing import List, Dict
from pydantic import BaseModel, Field, computed_field,field_validator,model_validator
import re
import difflib


class TestConstants:
    """テストの定数"""
    CORRECT_THRESHOLD = 90.0  # 一つのメッセージが正解と判定される閾値
    PASSING_THRESHOLD = 80.0  # テスト全体の合格閾値

class MessageScore(BaseModel):
    """メッセージごとのテストスコアを表すバリューオブジェクト"""
    message_order: int = Field(ge=1, description="メッセージの順番（1以上）")
    score: float = Field(ge=0, le=100, description="スコア（0〜100）")
    is_correct: bool
    user_answer: str
    correct_answer: str

    @model_validator(mode='after')
    def validate_score(self):
        if self.is_correct and self.score < TestConstants.CORRECT_THRESHOLD:
            raise ValueError("正解のスコアが {} 未満です".format(TestConstants.CORRECT_THRESHOLD))
        return self
   
    @staticmethod
    def tokenize(text: str) -> List[str]:
        # 前処理を追加
        text = text.strip()
        return re.findall(r'\b[\w\']+\b|[.,;!?]|\S', text)

    @staticmethod
    def get_matcher(user_answer: str, correct_answer: str):
        return difflib.SequenceMatcher(None, user_answer, correct_answer)

    @staticmethod
    def calculate_similarity(user_answer: str, correct_answer: str) -> float:
        """ユーザーの回答と正解の類似度を計算する"""
        matcher = MessageScore.get_matcher(user_answer, correct_answer)
        return round(matcher.ratio() * 100)

    @staticmethod
    def get_diff_blocks(user_answer: List[str], correct_answer: List[str]) -> List[tuple]:
        """ユーザーの回答と正解の差分を取得する"""
        matcher = difflib.SequenceMatcher(None, user_answer, correct_answer)
        return matcher.get_opcodes()

    @computed_field
    def get_tokenized_user_answer(self) -> List[str]:
        """ユーザーの回答をトークン化して返す"""
        return self.tokenize(self.user_answer)

    @computed_field
    def get_tokenized_correct_answer(self) -> List[str]:
        """正解の回答をトークン化して返す"""
        return self.tokenize(self.correct_answer)

    @classmethod
    def factory(cls, message_order: int, user_answer: str, correct_answer: str) -> 'MessageScore':
        """メッセージスコアを計算して作成する"""
        score = cls.calculate_similarity(user_answer, correct_answer)
        return cls(
            message_order=message_order,
            score=score,
            is_correct=score >= TestConstants.CORRECT_THRESHOLD,
            user_answer=user_answer,
            correct_answer=correct_answer
        )


class TestResult(BaseModel):
    """テスト結果を表すエンティティ（集約ルート）"""
    conversation_id: UUID
    test_number: int
    message_scores: List[MessageScore] = Field(ge=1,default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
        
    @field_validator('message_scores', mode='before')
    @classmethod
    def validate_message_scores(cls, value: List[MessageScore]):
        if not value:
            raise ValueError("メッセージスコアは1つ以上必要です")
        return value

    @computed_field
    def overall_score(self) -> float:
        """全体のスコアを計算する"""
        if not self.message_scores:
            return 0
        # 整数に変換
        return round(sum(score.score for score in self.message_scores) / len(self.message_scores))

    @computed_field
    def is_passing(self) -> bool:
        """合格判定（80%以上で合格）"""
        return self.overall_score() >= TestConstants.PASSING_THRESHOLD

    @classmethod
    def factory(cls, conversation_id: UUID, test_number: int,answers: List[Dict[str, str]]) -> 'TestResult':
        """ユーザーの回答リストからテスト結果を作成する"""
        result = cls(
            conversation_id=conversation_id,
            test_number=test_number
        )

        for answer in answers:
            score = MessageScore.factory(
                message_order=int(answer['message_order']),
                user_answer=answer['user_answer'],
                correct_answer=answer['correct_answer']
            )
            result.message_scores.append(score)

        return result