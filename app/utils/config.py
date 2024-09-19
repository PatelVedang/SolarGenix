import os
from pathlib import Path

from pydantic import EmailStr, Field, ValidationError
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    SECRET_KEY: str
    DEBUG: bool = Field(default=False)
    UNIT_TEST_USER_EMAIL: EmailStr = Field(default="example@yopmail.com")
    UNIT_TEST_USER_PASSWORD: str = Field(default="test@123")
    SQL_ENGINE: str = Field(default="django.db.backends.postgresql")
    SQL_DATABASE: str = Field(default="postgres")
    SQL_USER: str = Field(default="postgres")
    SQL_PASSWORD: str = Field(default="postgres")
    SQL_DATABASE_HOST: str = Field(default="localhost")
    SQL_DATABASE_PORT: int = Field(default=5432)
    EMAIL_HOST: str = Field(default="smtp.gmail.com")
    EMAIL_PORT: int = Field(default=465)
    EMAIL_USE_TLS: bool = Field(default=0)
    EMAIL_USE_SSL: bool = Field(default=1)
    EMAIL_BACKEND: str = Field(default="django_smtp_ssl.SSLEmailBackend")
    EMAIL_HOST_USER: EmailStr = Field(default="example@yopmail.com")
    EMAIL_HOST_PASSWORD: str = Field(default="Test@123")
    CSRF_TRUSTED_ORIGINS: str = Field(default="http://localhost:8000")
    CORS_ORIGIN_WHITELIST: str = Field(default="http://localhost:8000")
    PDF_DOWNLOAD_ORIGIN: str = Field(default="")
    HOST_URL: str = Field(default="http://localhost:8000")

    # Token Expiry
    # Token LifeLine in days
    AUTH_ACCESS_TOKEN_LIFELINE: int = Field(default=1)
    AUTH_REFRESH_TOKEN_LIFELINE: int = Field(default=30)
    # Token LifeLine in minutes
    AUTH_VERIFY_EMAIL_TOKEN_LIFELINE: int = Field(default=60)
    AUTH_RESET_PASSWORD_TOKEN_LIFELINE: int = Field(default=60)

    JWT_ALGORITHM: str = Field(default="HS256")
    # Google SSO
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SOCIAL_SECRET: str
    # Auth Throttling
    AUTH_THROTTLING_LIMIT: str
    # Super user
    SUPERUSER_EMAIL: str = Field(default="admin1@yopmail.com")
    # Swagger Authentication
    SWAGGER_AUTH_USERNAME: str
    SWAGGER_AUTH_PASSWORD: str
    SUPERUSER_PASSWORD: str  # Add this field if needed
    SUPERUSER_ADMIN: str

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")
        case_sensitive = True


def load_settings():
    env_file_path = os.path.join(BASE_DIR, ".env")
    if not os.path.isfile(env_file_path):
        raise FileNotFoundError(f"Missing required .env file at path: {env_file_path}")

    try:
        settings = Settings()
        print("Settings loaded successfully.")
        return settings
    except ValidationError as e:
        for error in e.errors():
            field = error["loc"][0]
            message = error["msg"]
            print(f"  - {field}: {message}", "error")
        raise e
        raise e
