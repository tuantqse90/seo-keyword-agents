import logging
import secrets

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://seo_user:seo_password@localhost:5432/seo_dashboard"

    @property
    def async_database_url(self) -> str:
        """Ensure database URL uses asyncpg driver (Railway provides postgresql://)."""
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    # LLM Provider: "anthropic" or "deepseek"
    llm_provider: str = "deepseek"

    # Anthropic
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"

    # Email (optional)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@seo-dashboard.local"
    notify_email: str = ""

    # Auth
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 72

    # CORS — comma-separated origins, e.g. "https://example.com,https://www.example.com"
    cors_origins: str = "http://localhost:3000"

    # Environment: "development" or "production"
    environment: str = "development"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    model_config = {
        "env_file": [".env", "../.env"],
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def get_cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()

# JWT secret validation
logger = logging.getLogger("app.config")
if not settings.jwt_secret:
    if settings.environment == "production":
        raise RuntimeError("JWT_SECRET must be set in production! Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\"")
    settings.jwt_secret = secrets.token_urlsafe(32)
    logger.warning("JWT_SECRET not set — generated random secret (will change on restart)")
elif settings.jwt_secret == "change-me-in-production" and settings.environment == "production":
    raise RuntimeError("JWT_SECRET is still the default value! Set a strong secret for production.")

# LLM key validation
if settings.environment == "production":
    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY not set but LLM_PROVIDER=anthropic")
    if settings.llm_provider == "deepseek" and not settings.deepseek_api_key:
        logger.warning("DEEPSEEK_API_KEY not set but LLM_PROVIDER=deepseek")
