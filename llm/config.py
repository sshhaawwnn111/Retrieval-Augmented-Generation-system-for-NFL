"""
Configuration management for LLM service using pydantic-settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service Configuration
    service_host: str = "0.0.0.0"
    service_port: int = 8001
    
    # vLLM Model Configuration
    model_name: str = "Qwen/Qwen2.5-7B-Instruct-AWQ"
    model_revision: str = "main"


    # CRITICAL: AWQ requires dtype="auto" and quantization="awq"
    model_dtype: str = "auto"
    quantization: Optional[str] = "awq"

    tensor_parallel_size: int = 1
    gpu_memory_utilization: float = 0.9
    max_model_len: int = 8192
    enable_prefix_caching: bool = True
    enable_chunked_prefill: bool = False

    # Generation Defaults
    default_max_tokens: int = 512
    default_temperature: float = 0.5
    default_top_p: float = 0.95
    
    # Service Settings
    log_level: str = "INFO"
    enable_metrics: bool = True
    
    # Optional HuggingFace Token
    hf_token: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        protected_namespaces = ("settings_",)


# Global settings instance
settings = Settings()
