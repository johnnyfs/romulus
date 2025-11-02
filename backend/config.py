from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Romulus"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://romulus:romulus@localhost:5433/romulus"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    FRONTEND_URL: str = "http://localhost:3001"

    # Security (add JWT secret, etc. as needed)
    # SECRET_KEY: str = "your-secret-key-here"
    # ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # MinIO / S3
    MINIO_ENDPOINT: str = "minio:9000"  # Internal Docker network endpoint
    MINIO_EXTERNAL_ENDPOINT: str = "localhost:9000"  # External endpoint for presigned URLs
    MINIO_EXTERNAL_ENDPOINT_FOR_CLIENT: str = "host.docker.internal:9000"  # How API reaches external endpoint
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False  # Use HTTPS
    MINIO_BUCKET: str = "assets"


settings = Settings()
