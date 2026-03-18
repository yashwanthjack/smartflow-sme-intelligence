# Application configuration
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartFlow"
    API_V1_STR: str = "/api/v1"
    # SQLite for development (no server required)
    # Change to PostgreSQL URL for production
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smartflow.db")
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
