"""
Configuration management for Aurora.
"""
from typing import Any, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Database
    DATABASE_URL: str = Field(default="postgresql://", env="DATABASE_URL")

    # Redis
    REDIS_URL: str = Field(default="", env="REDIS_URL")

    # JSON Web Token
    JWT_SECRET: str = Field(default="maybe-add-it-to-env")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 360
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: Any = Field(default=["http://localhost:5173"])

    # Ollama
    OLLAMA_HOST: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")

    # External APIs
    WEATHER_API_KEY: str = Field(default="", env="WEATHER_API_KEY")
    NEWS_API_KEY: str = Field(default="", env="NEWS_API_KEY")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        """Parse comma-separated string or list."""
        if isinstance(v, str):
            # Remove any whitespace and split by comma
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        # If it's already a list (from default or testing), return as-is
        if isinstance(v, list):
            return v
        # Fallback
        return []

    # Model
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# Global settings instance to import
settings = Settings()
