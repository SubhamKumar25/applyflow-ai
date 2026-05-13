from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "ApplyFlow AI"
    SECRET_KEY: str = "change-me"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "applyflow_ai"

    # JWT
    JWT_SECRET_KEY: str = "change-me-jwt"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440

    # AI
    AI_PROVIDER: Literal["openai", "gemini"] = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Automation
    DAILY_APPLY_LIMIT: int = 20
    PLAYWRIGHT_HEADLESS: bool = True

    # Notifications
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    # Scheduler
    SCHEDULER_ENABLED: bool = False
    SCHEDULER_CRON_HOUR: int = 9
    SCHEDULER_CRON_MINUTE: int = 0

    # Uploads
    MAX_RESUME_SIZE_MB: int = 10
    UPLOAD_DIR: str = "./resumes"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
