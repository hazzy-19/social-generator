"""
Core app configuration. Nothing but env-driven settings lives here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/quiet_authority"

    # DeepSeek AI endpoint
    deepseek_api_key: str = ""
    deepseek_api_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # image-service (Node wrapper around pexelkit)
    image_service_url: str = "http://localhost:4000"
    pexels_api_key: str = ""

    # App
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5174"]
    firebase_credentials_path: str | None = None
    tavily_api_key: str | None = None


settings = Settings()
