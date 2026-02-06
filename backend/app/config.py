# Application configuration
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartFlow"
    API_V1_STR: str = "/api/v1"
    # PostgreSQL connection - YASH server (@ in password encoded as %40)
    DATABASE_URL: str = "postgresql://postgres:yash%401234@localhost:5432/smartflow"
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
