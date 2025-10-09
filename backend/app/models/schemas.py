"""
Pydantic models for API requests and responses
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class LLMGenerateRequest(BaseModel):
    """Request model for LLM text generation"""
    prompt: str = Field(..., description="The input prompt for the LLM")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, description="Sampling temperature (0.0-1.0)")
    top_p: Optional[float] = Field(None, description="Top-p sampling parameter")
    stop_sequences: Optional[List[str]] = Field(None, description="Stop sequences")


class LLMGenerateResponse(BaseModel):
    """Response model for LLM text generation"""
    generated_text: str = Field(..., description="Generated text from LLM")
    model: str = Field(..., description="Model name/identifier")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage information")


class Text2SQLRequest(BaseModel):
    """Request model for text-to-SQL generation"""
    question: str = Field(..., description="Natural language question")
    schema_context: Optional[str] = Field(None, description="Database schema context")
    few_shot_examples: Optional[List[Dict[str, str]]] = Field(None, description="Few-shot examples")
    

class Text2SQLResponse(BaseModel):
    """Response model for text-to-SQL generation"""
    sql_query: str = Field(..., description="Generated SQL query")
    confidence: Optional[float] = Field(None, description="Confidence score")
    explanation: Optional[str] = Field(None, description="Query explanation")


class RetrievalRequest(BaseModel):
    """Request model for document/context retrieval"""
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, description="Number of results to retrieve")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters")


class RetrievalResponse(BaseModel):
    """Response model for retrieval"""
    results: List[Dict[str, Any]] = Field(..., description="Retrieved documents/contexts")
    total_count: int = Field(..., description="Total number of results")


class ReportGenerationRequest(BaseModel):
    """Request model for report generation"""
    query_results: Dict[str, Any] = Field(..., description="SQL query results")
    report_type: str = Field("summary", description="Type of report to generate")
    additional_context: Optional[str] = Field(None, description="Additional context")


class ReportGenerationResponse(BaseModel):
    """Response model for report generation"""
    report: str = Field(..., description="Generated report")
    report_type: str = Field(..., description="Type of report")
    s3_url: Optional[str] = Field(None, description="S3 URL if saved")
