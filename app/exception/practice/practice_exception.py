from fastapi import status
from app.core.exception.app_exception import AppException


class ConflictException(AppException):
    """コンフリクトに関する例外"""

    def __init__(self, detail: str = ""):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
