from functools import lru_cache
from typing import Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Department AI Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = (
        "postgresql+psycopg://department_ai:development-only@localhost:5432/department_ai"
    )
    jwt_secret_key: SecretStr = SecretStr("development-only-change-me-not-for-production")
    access_token_expire_minutes: int = Field(default=30, gt=0)

    @model_validator(mode="after")
    def validate_production_secret(self) -> Self:
        secret = self.jwt_secret_key.get_secret_value()
        if self.environment.lower() == "production" and (
            len(secret) < 32 or secret.startswith(("replace-", "development-only"))
        ):
            raise ValueError("Set JWT_SECRET_KEY to at least 32 random characters in production")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
