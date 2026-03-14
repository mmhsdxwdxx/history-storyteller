from pydantic_settings import BaseSettings

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
    DEFAULT_PROVIDER: str = "anthropic"

    class Config:
        env_file = ".env"

settings = Settings()
