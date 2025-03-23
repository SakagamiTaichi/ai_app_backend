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
        headers: Optional[dict] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


class InternalServerError(AppException):
    """内部サーバーエラー"""
    def __init__(self, detail: str = "エラーが発生しました。"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

def setup_exception_handlers(app: FastAPI) -> None:
    """グローバル例外ハンドラを設定"""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )