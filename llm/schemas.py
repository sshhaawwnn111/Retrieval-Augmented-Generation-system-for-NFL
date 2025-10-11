"""
Pydantic schemas for request and response models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GenerateTextRequest(BaseModel):
    """Request model for text generation."""
    
    prompt: str = Field(
        ...,
        description="The input prompt for text generation",
        min_length=1,
        examples=["Once upon a time"]
    )
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum number of tokens to generate",
        ge=1,
        le=4096
    )
    temperature: Optional[float] = Field(
        None,
        description="Sampling temperature (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )
    top_p: Optional[float] = Field(
        None,
        description="Nucleus sampling parameter",
        ge=0.0,
        le=1.0
    )
    top_k: Optional[int] = Field(
        None,
        description="Top-k sampling parameter",
        ge=-1
    )
    frequency_penalty: Optional[float] = Field(
        None,
        description="Frequency penalty (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )
    presence_penalty: Optional[float] = Field(
        None,
        description="Presence penalty (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )
    stop: Optional[List[str]] = Field(
        None,
        description="List of stop sequences"
    )
    stream: bool = Field(
        False,
        description="Whether to stream the response"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a short story about a robot learning to paint:",
                "max_tokens": 256,
                "temperature": 0.8,
                "top_p": 0.95
            }
        }


class GenerateTextResponse(BaseModel):
    """Response model for text generation."""
    
    text: str = Field(
        ...,
        description="The generated text"
    )
    prompt: str = Field(
        ...,
        description="The original prompt"
    )
    model: str = Field(
        ...,
        description="The model used for generation"
    )
    finish_reason: Optional[str] = Field(
        None,
        description="Reason for completion (stop, length, etc.)"
    )
    usage: Dict[str, int] = Field(
        default_factory=dict,
        description="Token usage statistics"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "In a small workshop, a robot named Artie discovered...",
                "prompt": "Write a short story about a robot learning to paint:",
                "model": "meta-llama/Llama-2-7b-chat-hf",
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": 12,
                    "completion_tokens": 156,
                    "total_tokens": 168
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    model: str = Field(..., description="Loaded model name")
    vllm_version: str = Field(..., description="vLLM version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model": "meta-llama/Llama-2-7b-chat-hf",
                "vllm_version": "0.3.0"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[Any] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Generation failed",
                "detail": "Maximum context length exceeded"
            }
        }
