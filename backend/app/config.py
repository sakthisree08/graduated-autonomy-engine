"""
Configuration management for the Graduated Autonomy Engine
Uses Pydantic Settings for type-safe configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./graduated_autonomy.db",
        env="DATABASE_URL",
    )
    
    # API
    api_version: str = Field(default="v1", env="API_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    
    # LLM Configuration
    llm_provider: str = Field(default="mock", env="LLM_PROVIDER")
    ollama_url: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    
    # Application
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Risk thresholds
    low_risk_threshold: int = Field(default=40)
    medium_risk_threshold: int = Field(default=70)
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Validate required settings
if settings.llm_provider == "groq" and not settings.groq_api_key:
    raise ValueError("GROQ_API_KEY required when using groq provider")