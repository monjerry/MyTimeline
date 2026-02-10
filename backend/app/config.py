"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Image source
    image_folder: Path = Path("/path/to/images")

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/images.db"

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2-vision"
    ollama_timeout: int = 120

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    # Processing
    batch_size: int = 10
    max_workers: int = 4

    # Caching
    cache_dir: Path = Path("./data/cache")
    thumbnail_sizes: str = "150,300,600"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @property
    def thumbnail_sizes_list(self) -> list[int]:
        """Parse thumbnail sizes as list of integers."""
        return [int(size) for size in self.thumbnail_sizes.split(",")]

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins as list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
