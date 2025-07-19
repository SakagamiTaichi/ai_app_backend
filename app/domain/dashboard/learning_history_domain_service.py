import datetime
from typing import List
from app.domain.dashboard.learning_history_entity import LearningHistoryEntity


class LearningHistoryDomainService:
    """
    学習履歴のドメインサービス.
    """

    def __init__(self, learning_histories: List[LearningHistoryEntity]):
        """
        コンストラクタ.

        :param learning_histories: 学習履歴のリスト
        """
        self.learning_histories = learning_histories
        self._validate_learning_histories()

    def get_total_learning_time(self) -> int:
        """
        総学習時間を取得.

        :return: 総学習時間（分単位）
        """
        total_time = sum(history.learningTime for history in self.learning_histories)
        return round(total_time / 60)  # 分単位に変換

    def get_total_learning_time_in_this_week(self) -> int:
        """
        今週の総学習時間を取得.

        :return: 今週の総学習時間（分単位）
        """
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        total_time = sum(
            history.learningTime
            for history in self.learning_histories
            if history.date >= start_of_week
        )
        return round(total_time / 60)

    def get_continuous_learning_days(self) -> int:
        """
        連続学習日数を取得.

        :return: 連続学習日数
        """
        if not self.learning_histories:
            return 0

        sorted_histories = sorted(self.learning_histories, key=lambda x: x.date)
        continuous_days = 1
        last_date = sorted_histories[0].date

        for history in sorted_histories[1:]:
            if (history.date - last_date).days == 1:
                continuous_days += 1
            elif (history.date - last_date).days > 1:
                break
            last_date = history.date

        return continuous_days

    def get_max_continuous_learning_days(self) -> int:
        """
        最大連続学習日数を取得.

        :return: 最大連続学習日数
        """
        if not self.learning_histories:
            return 0

        sorted_histories = sorted(self.learning_histories, key=lambda x: x.date)
        max_continuous_days = 1
        current_streak = 1
        last_date = sorted_histories[0].date

        for history in sorted_histories[1:]:
            if (history.date - last_date).days == 1:
                current_streak += 1
            elif (history.date - last_date).days > 1:
                max_continuous_days = max(max_continuous_days, current_streak)
                current_streak = 1
            last_date = history.date

        return max(max_continuous_days, current_streak)

    def _validate_learning_histories(self):
        """
        学習履歴の検証.

        :raises ValueError: 学習履歴が空の場合
        """
        # if not self.learning_histories:
        #     raise ValueError("学習履歴が空です。")

        # for history in self.learning_histories:
        #     if not isinstance(history, LearningHistoryEntity):
        #         raise ValueError("学習履歴はLearningHistoryEntityのインスタンスでなければなりません。")
