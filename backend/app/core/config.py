"""
Core app configuration. Nothing but env-driven settings lives here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/quiet_authority"

    # AI Provider routing ("gemini" or "nvidia")
    ai_provider: str = "nvidia"

    # Gemini AI endpoint
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # NVIDIA AI endpoint
    nvidia_api_key: str = ""
    nvidia_api_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.1-70b-instruct"

    # image-service (Node wrapper around pexelkit)
    image_service_url: str = "http://localhost:4000"
    pexels_api_key: str = ""

    # App
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5174"]
    firebase_credentials_path: str | None = None


settings = Settings()
