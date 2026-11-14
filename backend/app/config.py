
from functools import lru_cache
from typing import Annotated

from pydantic import Field, NoDecode, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    node_credentials_key: str = Field(
        min_length=44,
        max_length=44,
    )

    app_secret_key: str | None = None

    cors_origins: Annotated[
        list[str],
        NoDecode,
    ] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return value.split(",")

        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, origins: list[str]) -> list[str]:
        normalized = []

        for origin in origins:
            origin = origin.strip().rstrip("/")

            if not origin:
                continue

            if not origin.startswith(("http://", "https://")):
                raise ValueError(
                    "CORS origins must start with http:// or https://"
                )

            if any(char in origin for char in ("*", " ", "?", "#")):
                raise ValueError("Invalid CORS origin")

            if origin not in normalized:
                normalized.append(origin)

        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_node_encryption_key() -> str:
    return get_settings().node_credentials_key


def get_jwt_secret_key() -> str:
    secret_key = get_settings().app_secret_key

    if not secret_key:
        raise RuntimeError("APP_SECRET_KEY is not configured")

    if len(secret_key.encode("utf-8")) < 32:
        raise RuntimeError(
            "APP_SECRET_KEY must contain at least 32 bytes"
        )

    return secret_key
