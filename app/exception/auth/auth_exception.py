from fastapi import status
from app.core.exception.app_exception import AppException

class AuthenticationException(AppException):
    """認証に関する例外"""
    def __init__(self, detail: str = "パスワードもしくはIDが間違っています。"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class FailedToCreateUserException(AppException):
    """ユーザーの作成に失敗した場合の例外"""
    def __init__(self, detail: str = "ユーザーの作成に失敗しました"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class UserAlreadyExistsException(AppException):
    """ユーザーが既に存在する場合の例外"""
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"メールアドレス「{email}」は既に登録されています"
        )

