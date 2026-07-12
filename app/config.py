# app/config.py
import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variables"""
    
    # Application
    APP_NAME: str = Field("DynamicPortfolio", env="APP_NAME")
    APP_ENV: str = Field("development", env="APP_ENV")
    DEBUG: bool = Field(True, env="DEBUG")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    PORT: int = Field(5000, env="PORT")
    
    # OpenRouter
    OPENROUTER_API_KEY: str = Field(..., env="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = Field(
        "https://openrouter.ai/api/v1",
        env="OPENROUTER_BASE_URL"
    )
    OPENROUTER_MODEL: str = Field("openrouter/free", env="OPENROUTER_MODEL")
    OPENROUTER_TIMEOUT: int = Field(30, env="OPENROUTER_TIMEOUT")
    OPENROUTER_RETRY_ATTEMPTS: int = Field(3, env="OPENROUTER_RETRY_ATTEMPTS")
    
    # Database
    DATABASE_URL: str = Field("sqlite:///data/portfolio.db", env="DATABASE_URL")
    
    # GitHub
    GITHUB_TOKEN: Optional[str] = Field(None, env="GITHUB_TOKEN")
    GITHUB_WEBHOOK_SECRET: Optional[str] = Field(None, env="GITHUB_WEBHOOK_SECRET")
    GITHUB_API_URL: str = Field("https://api.github.com", env="GITHUB_API_URL")
    
    # LinkedIn
    LINKEDIN_EMAIL: Optional[str] = Field(None, env="LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD: Optional[str] = Field(None, env="LINKEDIN_PASSWORD")
    LINKEDIN_PROFILE_URL: Optional[str] = Field(None, env="LINKEDIN_PROFILE_URL")
    
    # Resume
    RESUME_STORAGE_URL: Optional[str] = Field(None, env="RESUME_STORAGE_URL")
    RESUME_JSON_URL: Optional[str] = Field(None, env="RESUME_JSON_URL")
    
    # Cache & Queue
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    CELERY_BROKER_URL: str = Field("redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field("redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # Security
    CORS_ALLOWED_ORIGINS: list = Field(
        ["http://localhost:3000"],
        env="CORS_ALLOWED_ORIGINS"
    )
    RATE_LIMIT: str = Field("100/hour", env="RATE_LIMIT")
    MAX_REQUEST_SIZE: int = Field(10 * 1024 * 1024, env="MAX_REQUEST_SIZE")
    
    # Monitoring
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_database_url(self) -> str:
        """Get database URL with proper format"""
        if self.DATABASE_URL.startswith("sqlite:///"):
            # Ensure data directory exists for SQLite
            import os
            db_path = self.DATABASE_URL.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return self.DATABASE_URL


settings = Settings()