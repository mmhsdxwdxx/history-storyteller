from pydantic_settings import BaseSettings
from pathlib import Path

# 尝试多个可能的 .env 位置
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_ROOT = Path(__file__).parent.parent

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@db:5432/history_storyteller"

    # AI Providers
    OPENAI_API_URL: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    ANTHROPIC_API_URL: str = ""
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    GEMINI_API_URL: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"

    # Default provider: openai, anthropic, or gemini
    DEFAULT_PROVIDER: str = "openai"

    class Config:
        env_file = [
            str(PROJECT_ROOT / ".env"),
            str(BACKEND_ROOT / ".env"),
            ".env"
        ]
        env_file_encoding = 'utf-8'

settings = Settings()
