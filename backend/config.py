from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, PostgresDsn, HttpUrl, validator
from typing import Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "FinmateAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[HttpUrl] = []
    
    # Frontend
    FRONTEND_ORIGIN: HttpUrl
    
    # Database
    DATABASE_URL: PostgresDsn
    
    # Security
    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenAI
    OPENAI_API_KEY: SecretStr
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Plaid
    PLAID_CLIENT_ID: SecretStr
    PLAID_SECRET: SecretStr
    PLAID_ENV: str = "sandbox"  # sandbox, development, production
    
    # Redis (for caching and rate limiting)
    REDIS_URL: Optional[str] = None
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "csv", "xlsx", "xls"}
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS Configuration
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database URL Validation
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str | None) -> str:
        if v is None:
            raise ValueError("DATABASE_URL is required")
        return v
    
    # Environment-specific settings
    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v
    
    # Plaid environment validation
    @validator("PLAID_ENV")
    def validate_plaid_env(cls, v: str) -> str:
        allowed = {"sandbox", "development", "production"}
        if v not in allowed:
            raise ValueError(f"PLAID_ENV must be one of {allowed}")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This function is cached to avoid reading the .env file multiple times.
    """
    return Settings()

# Create settings instance
settings = get_settings() 