from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"
    TEMPERATURE: float = 0.7
    ASYNC_DATABASE_URL: str = ""
    DATABASE_URL: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str = ""
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = ""
    ENVIRONMENT: str = ""

    # 認証関連の設定
    SECRET_KEY: str = ""  # JWT署名用の秘密鍵
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # Resend設定
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "noreply@eigoats.com"

    # 認証コード設定
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 10
    VERIFICATION_CODE_LENGTH: int = 6

    # フロントエンド設定
    FRONTEND_URL: str = "com.example.ai_english"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
