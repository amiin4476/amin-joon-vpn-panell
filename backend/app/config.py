
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    node_credentials_key: str = Field(
        min_length=44,
        max_length=44,
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
