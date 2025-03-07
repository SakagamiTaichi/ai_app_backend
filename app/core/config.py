from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recipe Generator API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for generating recipes based on ingredients"
    API_V1_STR: str = "/api/v1"
    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.7
    DATABASE_URL: str = ""
    ASYNC_DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str = ""
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()