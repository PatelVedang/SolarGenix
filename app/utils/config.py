from pydantic import  ValidationError, EmailStr
from pydantic_settings import BaseSettings
import os 


class Settings(BaseSettings):
    SECRET_KEY: str
    DEBUG: bool
    UNIT_TEST_USER_EMAIL: EmailStr
    UNIT_TEST_USER_PASSWORD: str
    SQL_ENGINE: str
    SQL_DATABASE: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_DATABASE_HOST: str
    SQL_DATABASE_PORT: int
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_USE_SSL: bool
    EMAIL_BACKEND: str
    EMAIL_HOST_USER: EmailStr
    EMAIL_HOST_PASSWORD: str
    CSRF_TRUSTED_ORIGINS: str
    CORS_ORIGIN_WHITELIST: str
    PDF_DOWNLOAD_ORIGIN: str
    
    # JWT Settings
    JWT_ACCESS_TOKEN_LIFETIME: int
    JWT_REFRESH_TOKEN_LIFETIME: int
    JWT_ALGORITHM: str
    


    class Config:
        env_file = ".env"
        case_sensitive = True

def load_settings():
    env_file_path = ".env"
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
            print(f"  - {field}: {message}","error")
        # print(f"Validation error: {e}")
        raise e
   