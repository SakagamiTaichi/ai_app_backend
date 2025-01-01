from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recipe Generator API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for generating recipes based on ingredients"
    API_V1_STR: str = "/api/v1"
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.7
    DATABASE_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()