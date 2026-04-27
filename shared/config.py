from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()