from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "staging", "production"] = "development"
    app_name: str = "NordxPOS"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173"

    database_url: str = Field(
        default="postgresql+asyncpg://nordxpos:nordxpos@localhost:5432/nordxpos"
    )

    secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    password_min_length: int = 8

    rate_limit_per_minute: int = 120

    upload_dir: str = "/data/uploads"
    max_upload_size_mb: int = 25

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@nordxpos.co.za"
    smtp_tls: bool = True

    default_currency: str = "ZAR"
    default_locale: str = "en-ZA"
    default_timezone: str = "Africa/Johannesburg"

    demo_mode: bool = True
    demo_admin_email: str = "admin@demo.nordxpos.co.za"
    demo_admin_password: str = "Demo@2026!"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> str:
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
