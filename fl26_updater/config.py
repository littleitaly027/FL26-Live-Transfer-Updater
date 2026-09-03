"""Configuration management for FL26 Live Transfer Updater."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # File paths
    EDIT_FILE: Optional[str] = None
    BACKUP_DIR: str = "./backups"
    OUTPUT_DIR: str = "./output"
    DATABASE_PATH: str = "./data/transfers.db"

    # Scan configuration
    SCAN_INTERVAL_MINUTES: int = 15
    DEEP_SCAN_INTERVAL_HOURS: int = 6

    # Confidence thresholds (0-100)
    AUTO_APPLY_THRESHOLD: int = 99
    REVIEW_THRESHOLD: int = 80

    # Logging
    LOG_LEVEL: str = "INFO"

    # Sources
    ENABLE_FOTMOB: bool = True
    ENABLE_TRANSFERMARKT: bool = False

    # Rate limits
    FOTMOB_RATE_LIMIT: int = 100
    FOTMOB_RATE_LIMIT_WINDOW_SECONDS: int = 3600

    # GitHub Actions (optional)
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_REPOSITORY: Optional[str] = None

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        Path(self.BACKUP_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

    def validate_edit_file(self) -> bool:
        """Check if EDIT file is configured and exists."""
        if not self.EDIT_FILE:
            return False
        return Path(self.EDIT_FILE).exists()
