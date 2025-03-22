# app/domain/entities/test_result.py
from datetime import datetime
from uuid import UUID
from typing import List, Dict
from dataclasses import dataclass, field

@dataclass
class MessageScore:
    """メッセージごとのテストスコアを表すバリューオブジェクト"""
    message_order: int
    score: float
    is_correct: bool
    user_answer: str
    correct_answer: str
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        import re
        text = text.strip()
        return re.findall(r'\b[\w\']+\b|[.,;!?]|\S', text)   

    @staticmethod
    def get_matcher( user_answer: str, correct_answer: str):
        import difflib
        return difflib.SequenceMatcher(None, user_answer, correct_answer)

    @staticmethod
    def calculate_similarity(user_answer: str, correct_answer: str) -> float:
        """ユーザーの回答と正解の類似度を計算する"""
        
        matcher = MessageScore.get_matcher(user_answer, correct_answer)
        return round(matcher.ratio() * 100)
    
    @staticmethod
    def get_diff_blocks(user_answer: List[str], correct_answer: List[str]) -> List[tuple]:
        """ユーザーの回答と正解の差分を取得する"""
        import difflib
        
        matcher = difflib.SequenceMatcher(None,user_answer, correct_answer)
        return matcher.get_opcodes()
    

    @property
    def get_tokenized_user_answer(self) -> List[str]:
        """ユーザーの回答をトークン化して返す"""
        return self.tokenize(self.user_answer)
    
    @property
    def get_tokenized_correct_answer(self) -> List[str]:
        """正解の回答をトークン化して返す"""
        return self.tokenize(self.correct_answer)
    

    @classmethod
    def create(cls, message_order: int, user_answer: str, correct_answer: str) -> 'MessageScore':
        """メッセージスコアを計算して作成する"""
        score = cls.calculate_similarity(user_answer, correct_answer)
        return cls(
            message_order=message_order,
            score=score,
            is_correct=score >= 90.0,
            user_answer=user_answer,
            correct_answer=correct_answer
        )

@dataclass
class TestResult:
    """テスト結果を表すエンティティ（集約ルート）"""
    conversation_id: UUID
    test_number: int
    message_scores: List[MessageScore] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def overall_score(self) -> float:
        """全体のスコアを計算する"""
        if not self.message_scores:
            return 0
        # 整数に変換
        return round(sum(score.score for score in self.message_scores) / len(self.message_scores))
    
    @property
    def is_passing(self) -> bool:
        """合格判定（80%以上で合格）"""
        return self.overall_score >= 80.0
    
    def add_message_score(self, message_score: MessageScore) -> None:
        """メッセージスコアを追加する"""
        self.message_scores.append(message_score)
    
    @classmethod
    def create_from_answers(cls, conversation_id: UUID, test_number: int, 
                           answers: List[Dict[str, str]]) -> 'TestResult':
        """ユーザーの回答リストからテスト結果を作成する"""
        result = cls(
            conversation_id=conversation_id,
            test_number=test_number
        )
        
        for answer in answers:
            score = MessageScore.create(
                message_order=int(answer['message_order']),
                user_answer=answer['user_answer'],
                correct_answer=answer['correct_answer']
            )
            result.add_message_score(score)
            
        return result