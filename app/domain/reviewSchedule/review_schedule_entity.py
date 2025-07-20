import datetime
from typing import List, Self
from uuid import UUID
from pydantic import BaseModel, Field


class RecallCardConstants:
    """暗記カードの定数"""

    BASIC_ADD_DEADLINE: datetime.timedelta = datetime.timedelta(days=3)

    # 最新スコア係数
    LATEST_SCORE_MULTIPLIERS = {
        (90, 100): 3.0,
        (80, 89): 2.0,
        (60, 79): 1.0,
        (40, 59): 0.4,
        (0, 39): 0.2,
    }


class ReviewScheduleEntity(BaseModel):
    """復習スケジュールエンティティ"""

    reviewScheduleId: UUID = Field(..., description="復習スケジュールID")
    userId: UUID = Field(..., description="ユーザーID")
    quizId: UUID = Field(..., description="クイズID")
    reviewDeadLine: datetime.datetime = Field(..., description="復習期限")

    def update(self, scores: List[int]) -> Self:
        """復習スケジュールを更新する"""
        if not scores:
            return self

        # 復習期限のプラス = 基本期間 × 最新スコア係数 × 連続性係数 × 平均補正係数
        latest_score_multiplier = self._get_latest_score_multiplier(scores[-1])
        continuity_multiplier = self._get_continuity_multiplier(scores)
        average_correction_multiplier = self._get_average_correction_multiplier(scores)

        # 追加期間を計算
        multiplier = (
            latest_score_multiplier
            * continuity_multiplier
            * average_correction_multiplier
        )
        add_deadline_timedelta = RecallCardConstants.BASIC_ADD_DEADLINE * multiplier

        # 現在日時から復習期限を計算
        new_deadline = datetime.date.today() + add_deadline_timedelta

        # 新しいインスタンスを返す
        return self.model_copy(update={"reviewDeadLine": new_deadline})

    def _get_latest_score_multiplier(self, latest_score: int) -> float:
        """最新スコアに基づく係数を取得"""
        for (
            min_score,
            max_score,
        ), multiplier in RecallCardConstants.LATEST_SCORE_MULTIPLIERS.items():
            if min_score <= latest_score <= max_score:
                return multiplier
        return RecallCardConstants.LATEST_SCORE_MULTIPLIERS[(0, 29)]  # デフォルト

    def _get_continuity_multiplier(self, scores: List[int]) -> float:
        """連続性に基づく係数を取得"""
        if len(scores) < 2:
            return 1.0

        # 連続高得点（80点以上）をチェック
        high_score_streak = 0
        for score in reversed(scores):
            if score >= 80:
                high_score_streak += 1
            else:
                break

        # 連続低得点（50点未満）をチェック
        low_score_streak = 0
        for score in reversed(scores):
            if score < 50:
                low_score_streak += 1
            else:
                break

        # 連続高得点の場合
        if high_score_streak >= 4:
            return 2.0
        elif high_score_streak == 3:
            return 1.5
        elif high_score_streak == 2:
            return 1.2

        # 連続低得点の場合
        elif low_score_streak >= 3:
            return 0.5
        elif low_score_streak == 2:
            return 0.7

        return 1.0

    def _get_average_correction_multiplier(self, scores: List[int]) -> float:
        """平均スコアに基づく補正係数を取得"""
        if not scores:
            return 1.0

        average_score = sum(scores) / len(scores)

        if average_score >= 80:
            return 1.2
        elif average_score >= 60:
            return 1.0
        elif average_score >= 40:
            return 0.8
        else:
            return 0.6
