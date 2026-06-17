from __future__ import annotations

from pathlib import Path

from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str
    walrus_publisher: str
    walrus_aggregator: str
    database_url: str = "sqlite:///hottake.db"
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("openai_api_key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v.startswith("sk-"):
            raise ValueError("Invalid OpenAI key format — must start with 'sk-'")
        return v

    @field_validator("walrus_publisher", "walrus_aggregator")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError("Must be a valid HTTP or HTTPS URL")
        return v.rstrip("/")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                import json
                return json.loads(v)
            if "," in v:
                return [o.strip() for o in v.split(",") if o.strip()]
            return [v]
        raise ValueError(f"Unsupported type for cors_origins: {type(v).__name__}")


settings = Settings()
