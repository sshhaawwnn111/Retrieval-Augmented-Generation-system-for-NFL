"""
Configuration Management for RavensRotoWire Backend
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "RavensRotoWire"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.cloudfront.net",
        "https://*.amplifyapp.com",
        "https://app.ravens-rotowire.com",
        "https://ravens-rotowire.com",
    ]
    
    # AWS Settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Database Settings (Aurora PostgreSQL)
    DATABASE_NAME: Optional[str] = os.getenv("DATABASE_NAME", "Ravensrotowire")
    DATABASE_USER: Optional[str] = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: Optional[str] = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST: Optional[str] = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_READER_HOST: Optional[str] = os.getenv("DATABASE_READER_HOST")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_SSL: bool = os.getenv("DATABASE_SSL", "true").lower() == "true"
    USE_SECRETS_MANAGER: bool = os.getenv("USE_SECRETS_MANAGER", "true").lower() == "true"
    DATABASE_SECRET_NAME: Optional[str] = os.getenv("DATABASE_SECRET_NAME", "rds!cluster-8d6049d8-e87d-4a83-a77d-63030ce4d651")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
