from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"
    TEMPERATURE: float = 0.7
    ASYNC_DATABASE_URL: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str = ""
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = ""
    ENVIRONMENT: str = ""

    # 認証関連の設定
    SECRET_KEY: str = ""  # JWT署名用の秘密鍵
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()