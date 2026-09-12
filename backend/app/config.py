from functools import lru_cache
from typing import List, Union
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    PROJECT_NAME: str = "DineSpace Backend"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api"

    # CORS configuration - list of allowed origins or comma-separated string
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
    ]

    # MongoDB configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "dinespace"
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 2000

    # JWT Authentication configuration
    JWT_SECRET_KEY: str = "dinespace-dev-secret-key-change-in-production-123456789"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Application Timezone (for daily dining operations)
    TIMEZONE: str = "Asia/Kolkata"

    # Dining Hall Virtual Capacity
    TOTAL_SEATS: int = 100

    # Default Dining Hall Name
    DEFAULT_DINING_HALL: str = "Central Mess"

    # Seat Expiration and Background Sweeper Configuration
    SEAT_TIMEOUT_MINUTES: int = Field(
        default=25,
        validation_alias=AliasChoices("DINESPACE_SEAT_TIMEOUT_MINUTES", "SEAT_TIMEOUT_MINUTES"),
        description="Duration in minutes after which an active occupied seat is expired",
    )
    SWEEPER_INTERVAL_SECONDS: int = Field(
        default=60,
        validation_alias=AliasChoices("DINESPACE_SWEEPER_INTERVAL_SECONDS", "SWEEPER_INTERVAL_SECONDS"),
        description="Background worker polling interval in seconds",
    )

    @field_validator("SEAT_TIMEOUT_MINUTES", "SWEEPER_INTERVAL_SECONDS")
    @classmethod
    def validate_positive_intervals(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Timeout and sweeper intervals must be greater than zero")
        return v

    @field_validator("TOTAL_SEATS")
    @classmethod
    def validate_total_seats(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("TOTAL_SEATS must be greater than zero")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Parse comma-separated origins if provided as a string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        raise ValueError("Invalid format for CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of the settings."""
    return Settings()
