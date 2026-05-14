from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = ""
    azure_openai_chat_deployment: str = ""
    azure_openai_embedding_deployment: str = ""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/semantic_kernel"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def missing_chat_settings(self) -> list[str]:
        required_values = {
            "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
            "AZURE_OPENAI_API_KEY": self.azure_openai_api_key,
            "AZURE_OPENAI_CHAT_DEPLOYMENT": self.azure_openai_chat_deployment,
        }
        return [name for name, value in required_values.items() if not value]

    def is_chat_configured(self) -> bool:
        return not self.missing_chat_settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
