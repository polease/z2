"""
Configuration for web dashboard
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/z2_platform"

    # API
    API_PREFIX: str = "/api"
    API_TITLE: str = "Z2 AI Knowledge Distillery Platform API"
    API_VERSION: str = "1.0.0"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Job Queue
    MAX_CONCURRENT_JOBS: int = 2

    # Storage paths
    STORAGE_PATH: str = "./storage"

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
