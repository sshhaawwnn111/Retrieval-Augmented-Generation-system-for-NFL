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
    
    # vLLM Service Configuration (for self-hosted LLM)
    VLLM_MODEL_NAME: str = os.getenv("VLLM_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    VLLM_SERVICE_URL: str = Field(
        default="http://18.226.180.255:8001",
        description="Base URL for self-hosted vLLM service"
    )
    RERANKER_SERVICE_URL: str = Field(
        default="http://localhost:8002",
        description="Base URL for reranker service"
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
    DATABASE_NAME: Optional[str] = os.getenv("DATABASE_NAME", "Ravensrotowire")
    DATABASE_USER: Optional[str] = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: Optional[str] = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST: Optional[str] = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_READER_HOST: Optional[str] = os.getenv("DATABASE_READER_HOST")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_SSL: bool = os.getenv("DATABASE_SSL", "true").lower() == "true"
    USE_SECRETS_MANAGER: bool = os.getenv("USE_SECRETS_MANAGER", "true").lower() == "true"
    DATABASE_SECRET_NAME: Optional[str] = os.getenv("DATABASE_SECRET_NAME", "rds!cluster-8d6049d8-e87d-4a83-a77d-63030ce4d651")

    # S3 Settings
    S3_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "ravens-rotowire-reports")
    S3_REPORTS_PREFIX: str = os.getenv("S3_REPORTS_PREFIX", "reports/")
    S3_RAW_DATA_PREFIX: str = os.getenv("S3_RAW_DATA_PREFIX", "raw_data/")
    S3_EMBEDDINGS_PREFIX: str = os.getenv("S3_EMBEDDINGS_PREFIX", "embeddings/")


    
    # CloudWatch Settings
    CLOUDWATCH_LOG_GROUP: str = os.getenv("CLOUDWATCH_LOG_GROUP", "/aws/ecs/ravens-rotowire")
    CLOUDWATCH_LOG_STREAM: str = os.getenv("CLOUDWATCH_LOG_STREAM", "backend")
    
    # pgvector Settings
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    
    # Reranker Service Configuration
    RERANKER_SERVICE_URL: Optional[str] = os.getenv("RERANKER_SERVICE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
