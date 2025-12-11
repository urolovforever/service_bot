"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Bot Configuration
    BOT_TOKEN: str
    ADMIN_IDS: str

    # Database Configuration
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Application Settings
    DEFAULT_LANGUAGE: str = "ru"
    LOG_LEVEL: str = "INFO"
    SESSION_TTL: int = 3600

    # Anti-spam settings
    CONTACT_LIMIT_PER_HOUR: int = 10
    RATING_LIMIT_PER_DAY: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Get database URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        """Get Redis URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def admin_list(self) -> List[int]:
        """Get list of admin IDs"""
        return [int(admin_id.strip()) for admin_id in self.ADMIN_IDS.split(",") if admin_id.strip()]


settings = Settings()
