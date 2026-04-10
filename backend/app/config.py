"""LUXOR9 Backend - Core Configuration"""
import secrets
import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional
from pydantic import field_validator, model_validator


class Settings(BaseSettings):
    # Core
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Security - Production enforcement
    secret_key: str = ""  # MUST be set in production
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS - More secure default
    cors_origins: str = ""  # Empty = block all origins by default
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    cors_allow_headers: str = "Content-Type,Authorization,X-Request-ID"
    
    # API Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    rate_limit_burst: int = 10

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/luxor9"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50

    # AI Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    groq_api_key: str = ""

    # Model Configuration
    default_model: str = "gpt-4o-mini"
    reasoning_model: str = "gpt-4o"
    fallback_models: str = "gpt-4o-mini,claude-3-haiku-20240307,llama-3-70b-8192"

    # Rate Limits
    openai_rpm: int = 10000
    anthropic_rpm: int = 5000
    groq_rpm: int = 30

    # Token Budgets
    prime_token_budget: int = 50000
    csuite_token_budget: int = 20000
    vp_token_budget: int = 10000
    manager_token_budget: int = 5000
    worker_token_budget: int = 2000

    # Agent Cycles (seconds)
    prime_cycle: int = 60
    csuite_cycle: int = 30
    vp_cycle: int = 60
    manager_cycle: int = 45
    worker_cycle: int = 30

    # Stream Configuration
    total_streams: int = 100
    streams_per_category: int = 10

    # Revenue
    daily_revenue_target: float = 1000.0
    monthly_revenue_target: float = 30000.0

    # External Services
    stripe_api_key: str = ""
    resend_api_key: str = ""
    slack_webhook_url: str = ""

    # Monitoring
    sentry_dsn: str = ""
    health_check_interval: int = 30
    metrics_interval: int = 1

    # Validation
    @model_validator(mode="after")
    def validate_production_settings(self):
        """Ensure production has secure settings"""
        if self.environment == "production":
            if not self.secret_key or self.secret_key == "":
                raise ValueError("secret_key MUST be set in production")
            if len(self.secret_key) < 32:
                raise ValueError("secret_key must be at least 32 characters in production")
            if self.cors_origins == "*":
                raise ValueError("cors_origins cannot be '*' in production")
            if self.debug:
                raise ValueError("debug must be False in production")
        return self

    @field_validator("secret_key", mode="before")
    @classmethod
    def generate_secret_key(cls, v):
        """Auto-generate secure secret key if not provided"""
        if not v or v == "":
            return secrets.token_urlsafe(64)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def cors_methods_list(self) -> List[str]:
        return [m.strip() for m in self.cors_allow_methods.split(",")]

    @property
    def cors_headers_list(self) -> List[str]:
        return [h.strip() for h in self.cors_allow_headers.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ("development", "dev")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Convenience import
settings = get_settings()
