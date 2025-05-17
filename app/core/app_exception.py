from fastapi import status
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """アプリケーションのベース例外クラス"""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Internal server error",
        headers: Optional[dict] = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


class BadRequestError(AppException):
    """不正なリクエスト"""

    def __init__(self, detail: str = "不正なリクエストです。"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedError(AppException):
    """認証エラー"""

    def __init__(self, detail: str = "認証に失敗しました。"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenError(AppException):
    """アクセス拒否"""

    def __init__(self, detail: str = "アクセスが拒否されました。"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(AppException):
    """リソースが見つからない"""

    def __init__(self, detail: str = "リソースが見つかりません。"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(AppException):
    """リソースの競合"""

    def __init__(self, detail: str = "リソースの競合が発生しました。"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InternalServerError(AppException):
    """内部サーバーエラー"""

    def __init__(self, detail: str = "サーバーエラーが発生しました。"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class ServiceUnavailableError(AppException):
    """サービス利用不可"""

    def __init__(self, detail: str = "サービスが利用できません。"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


def setup_exception_handlers(app: FastAPI) -> None:
    """グローバル例外ハンドラを設定"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
