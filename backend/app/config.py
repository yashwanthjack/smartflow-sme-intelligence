# Application configuration
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartFlow"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./smartflow.db"
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()