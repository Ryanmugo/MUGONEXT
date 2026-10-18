"""
=========================================================
MUGONEXT
Application Configuration
=========================================================
"""

from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


# C:\MugoNEXT\Backend
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    and the Backend/.env file.
    """

    APP_NAME: str = "MUGONEXT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str
    JWT_SECRET: str

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OPENAI_API_KEY: str | None = None

    UPLOAD_FOLDER: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024

    DEFAULT_FORECAST_DAYS: int = 30
    TOP_K_RESULTS: int = 5

    MODEL_DEVICE: str = "cpu"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()