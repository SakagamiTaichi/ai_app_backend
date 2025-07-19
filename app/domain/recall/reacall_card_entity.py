import datetime
import difflib
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from typing_extensions import Self

from app.core.app_exception import BadRequestError
from app.domain.auth.user_entity import UserEntity


class RecallCardConstants:
    """暗記カードの定数"""

    REVIEW_DEADLINE_COEFFICIENT: float = 3.2  # 復習期限の計算に使用する係数
    CORRECT_POINT_DECREMENT: int = 5  # 不正解時に減らす正解ポイントの値
    CORRECT_THRESHOLD: float = 90.0  # 正解とみなす類似度の閾値（％）


class RecallCardEntity(BaseModel):
    # frozen=Trueでイミュータブルにする
    model_config = {"frozen": True}

    recallCardId: UUID = Field(..., description="暗記カードID")
    userId: UUID = Field(..., description="ユーザーID")
    question: str = Field(..., description="質問")
    answer: str = Field(..., description="答案")
    correctPoint: int = Field(..., ge=0, description="正解ポイント")
    reviewDeadline: datetime.datetime = Field(..., description="復習期限")

    @staticmethod
    def calculate_similarity(user_answer: str, correct_answer: str) -> float:
        """ユーザーの回答と正解の類似度を計算する"""
        matcher = difflib.SequenceMatcher(None, user_answer, correct_answer)
        return round(matcher.ratio() * 100)

    def update_by_user_answer(self, user_answer: str) -> Self:
        """ユーザーの回答に基づいて暗記カードを更新する"""
        # 類似度を計算
        similarity = self.calculate_similarity(user_answer, self.answer)

        # 類似度が閾値以上なら正解とみなす
        if similarity >= RecallCardConstants.CORRECT_THRESHOLD:
            return self._updateCorrectRecallCardEntity()
        else:
            return self._updateIncorrectRecallCardEntity()

    def _updateCorrectRecallCardEntity(self) -> Self:
        """正答した場合の復習期限を更新する"""
        """以下、復習期限の更新ルール"""
        # 1. 正解ポイントを1増やす
        # 2. 更新期限に対して（正解ポイント）の{REVIEW_DEADLINE_COEFFICIENT}乗分後加算する。

        updated_correct_point = self.correctPoint + 1

        # 復習期限の計算ロジック
        updated_review_deadline = self.reviewDeadline + datetime.timedelta(
            minutes=updated_correct_point
            ** RecallCardConstants.REVIEW_DEADLINE_COEFFICIENT
        )

        # 新しいインスタンスを作成して返す
        return self.__class__(
            recallCardId=self.recallCardId,
            userId=self.userId,
            question=self.question,
            answer=self.answer,
            correctPoint=updated_correct_point,
            reviewDeadline=updated_review_deadline,
        )

    def _updateIncorrectRecallCardEntity(self) -> Self:
        """不正解の場合の復習期限を更新する"""
        """以下、復習期限の更新ルール"""
        # 1. 正解ポイントを{CORRECT_POINT_DECREMENT}分減らす。
        # 2. 更新期限は変更しない。

        # 正解ポイントが負数にならないように制御
        updated_correct_point = max(
            0, self.correctPoint - RecallCardConstants.CORRECT_POINT_DECREMENT
        )

        # 新しいインスタンスを作成して返す
        return self.__class__(
            recallCardId=self.recallCardId,
            userId=self.userId,
            question=self.question,
            answer=self.answer,
            correctPoint=updated_correct_point,
            reviewDeadline=self.reviewDeadline,
        )


class TestResultDomainServie:
    """テスト結果のドメインサービス"""

    @staticmethod
    def validate(recall_cards: List[RecallCardEntity], users: List[UserEntity]) -> None:
        """データの整合性の確認を行う"""

        user_ids = {user.userId for user in users}
        for card in recall_cards:
            if card.userId not in user_ids:
                raise BadRequestError(detail=f"有効なユーザーを指定してください。")
