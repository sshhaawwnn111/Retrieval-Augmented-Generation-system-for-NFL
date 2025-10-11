"""
Configuration Management for RavensRotoWire Backend
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


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
        "https://*.amplifyapp.com"
    ]
    
    # AWS Settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # SageMaker Settings
    SAGEMAKER_ENDPOINT_NAME: Optional[str] = os.getenv("SAGEMAKER_ENDPOINT_NAME")
    SAGEMAKER_TIMEOUT: int = int(os.getenv("SAGEMAKER_TIMEOUT", "120"))
    SAGEMAKER_MAX_RETRIES: int = int(os.getenv("SAGEMAKER_MAX_RETRIES", "3"))
    
    # vLLM Service Configuration (for self-hosted LLM)
    VLLM_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        description="Base URL for self-hosted vLLM service"
    )
    VLLM_TIMEOUT: float = Field(
        default=120.0,
        description="Timeout for vLLM service requests in seconds"
    )
    VLLM_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum number of retries for vLLM service requests"
    )
    
    # LLM Settings
    LLM_MODEL_TYPE: str = os.getenv("LLM_MODEL_TYPE", "vllm")  # vllm or ollama
    LLM_MAX_TOKENS: int = Field(default=512, description="Default max tokens to generate")
    LLM_TEMPERATURE: float = Field(default=0.7, description="Default sampling temperature")
    LLM_TOP_P: float = Field(default=0.95, description="Default top-p sampling")
    
    # Database Settings (Aurora PostgreSQL)
    DATABASE_HOST: Optional[str] = os.getenv("DATABASE_HOST")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: Optional[str] = os.getenv("DATABASE_NAME", "ravens_db")
    DATABASE_USER: Optional[str] = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: Optional[str] = os.getenv("DATABASE_PASSWORD")
    DATABASE_SSL: bool = os.getenv("DATABASE_SSL", "true").lower() == "true"
    
    # S3 Settings
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")
    S3_REPORTS_PREFIX: str = os.getenv("S3_REPORTS_PREFIX", "reports/")
    S3_RAW_DATA_PREFIX: str = os.getenv("S3_RAW_DATA_PREFIX", "raw_data/")
    S3_EMBEDDINGS_PREFIX: str = os.getenv("S3_EMBEDDINGS_PREFIX", "embeddings/")
    
    # CloudWatch Settings
    CLOUDWATCH_LOG_GROUP: str = os.getenv("CLOUDWATCH_LOG_GROUP", "/aws/ecs/ravens-rotowire")
    CLOUDWATCH_LOG_STREAM: str = os.getenv("CLOUDWATCH_LOG_STREAM", "backend")
    
    # pgvector Settings
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
