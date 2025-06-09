import os
from pathlib import Path

from pydantic import EmailStr, Field, ValidationError
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # ::::::::::::: General :::::::::::::
    SECRET_KEY: str
    DEBUG: bool = Field(default=False)

    # ::::::::::::: DB Configuration :::::::::::::
    SQL_ENGINE: str = Field(default="django.db.backends.postgresql")
    SQL_DATABASE: str = Field(default="postgres")
    SQL_USER: str = Field(default="postgres")
    SQL_PASSWORD: str = Field(default="postgres")
    SQL_DATABASE_HOST: str = Field(default="localhost")
    SQL_DATABASE_PORT: int = Field(default=5432)

    # :::::::::::::: Email settings :::::::::::::
    EMAIL_HOST: str = Field(default="smtp.gmail.com")
    EMAIL_PORT: int = Field(default=465)
    EMAIL_USE_TLS: bool = Field(default=0)
    EMAIL_USE_SSL: bool = Field(default=1)
    EMAIL_BACKEND: str = Field(default="django_smtp_ssl.SSLEmailBackend")
    EMAIL_HOST_USER: EmailStr = Field(default="example@yopmail.com")
    EMAIL_HOST_PASSWORD: str = Field(default="Test@123")
    EMAIL_FORM_NAME: str

    # :::::::::::::: CSRF and CORS :::::::::::::
    CSRF_TRUSTED_ORIGINS: str = Field(default="http://localhost:8000")
    CORS_ORIGIN_WHITELIST: str = Field(default="http://localhost:8000")

    # :::::::::::::: Request Throttling :::::::::::::
    AUTH_THROTTLING_LIMIT: str

    # ::::::::::::: Unit test :::::::::::::
    UNIT_TEST_USER_EMAIL: EmailStr = Field(default="example@yopmail.com")
    UNIT_TEST_USER_PASSWORD: str = Field(default="test@123")

    # ::::::::::::: Google OAuth :::::::::::::
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # ::::::::::::: Configs :::::::::::::
    FRONTEND_URL: str = Field(default="http://localhost:8000")
    SUPERUSER_EMAIL: str = Field(default="admin1@yopmail.com")
    PROJECT_TITLE: str

    # ::::::::::::: Swagger Authentication :::::::::::::
    SWAGGER_AUTH_USERNAME: str
    SWAGGER_AUTH_PASSWORD: str
    JWT_ALGORITHM: str = Field(default="HS256")

    # ::::::::::::: Token Expiry :::::::::::::
    # Values in Days
    AUTH_ACCESS_TOKEN_DAYS: int = Field(default=1)
    AUTH_REFRESH_TOKEN_DAYS: int = Field(default=30)
    # Values in Minutes
    AUTH_VERIFY_EMAIL_TOKEN_MINUTES: int = Field(default=60)
    AUTH_RESET_PASSWORD_TOKEN_MINUTES: int = Field(default=60)
    OTP_EXPIRY_MINUTES: int = Field(default=1)

    # CELERY_BROKER_URL: str = Field(default=None)

    # ::::::::::::: Cognito :::::::::::::
    AUTH_TYPE: str = Field(default="simplejwt")
    AWS_REGION: str | None = Field(default=None)
    COGNITO_USER_POOL_ID: str | None = Field(default=None)
    COGNITO_CLIENT_ID: str | None = Field(default=None)
    COGNITO_CLIENT_SECRET: str | None = Field(default=None)
    COGNITO_DOMAIN: str | None = Field(default=None)
    COGNITO_REDIRECT_URI: str | None = Field(default=None)
    AWS_ACCESS_KEY_ID: str | None = Field(default=None)
    AWS_SECRET_ACCESS_KEY: str | None = Field(default=None)
    ENABLE_2FA: bool = Field(default=0)

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")
        case_sensitive = True


def load_settings():
    env_file_path = os.path.join(BASE_DIR, ".env")
    if not os.path.isfile(env_file_path):
        raise FileNotFoundError(f"Missing required .env file at path: {env_file_path}")

    try:
        settings = Settings()
        validate_auth_type(settings)

        for field in settings.__fields__.keys():
            if not getattr(settings, field):
                # Assign default values if they are empty
                default_value = settings.__fields__[field].default
                setattr(settings, field, default_value)
        print("Settings loaded successfully.")
        return settings
    except ValidationError as e:
        for error in e.errors():
            field = error["loc"][0]
            message = error["msg"]
            print(f"  - {field}: {message}", "error")
        raise e


def validate_auth_type(settings: Settings):
    if settings.AUTH_TYPE == "cognito":
        required_fields = [
            "AWS_REGION",
            "COGNITO_USER_POOL_ID",
            "COGNITO_CLIENT_ID",
            "COGNITO_CLIENT_SECRET",
            "COGNITO_DOMAIN",
            "COGNITO_REDIRECT_URI",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
        ]
        missing = [field for field in required_fields if not getattr(settings, field)]
        if missing:
            raise ValueError(f"Missing required Cognito fields: {', '.join(missing)}")
