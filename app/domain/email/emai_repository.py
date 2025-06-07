from abc import ABC, abstractmethod


class EmailRepository(ABC):
    """認証機能のリポジトリインターフェース"""

    @abstractmethod
    async def send_verification_code(self, email: str, code: str) -> bool:
        """メールアドレスの確認メールを送信する"""
        pass
