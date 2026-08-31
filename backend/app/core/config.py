from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database_url: str = "sqlite:///./recap.db"

    razorpay_webhook_secret: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-luna"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:4b"

    ai_agent_enabled: bool = False
    ai_provider: str = "ollama"


@lru_cache
def get_settings() -> Settings:
    return Settings()