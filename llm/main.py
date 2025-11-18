"""
vLLM Service - FastAPI application for high-throughput LLM inference.

This service provides a production-ready text generation endpoint using vLLM.
"""
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from vllm import AsyncLLMEngine, SamplingParams, AsyncEngineArgs
from vllm import __version__ as vllm_version

from config import settings
from schemas import (
    GenerateTextRequest,
    GenerateTextResponse,
    HealthResponse,
    ErrorResponse
)


# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global engine instance
engine: Optional[AsyncLLMEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    global engine
    global reranker_service
    
    # Startup: Initialize vLLM engine
    logger.info("Initializing vLLM engine...")
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"Tensor Parallel Size: {settings.tensor_parallel_size}")
    logger.info(f"Data Type: {settings.model_dtype}")
    
    try:
        engine_args = AsyncEngineArgs(
            model=settings.model_name,
            revision=settings.model_revision,
            dtype=settings.model_dtype,
            tensor_parallel_size=settings.tensor_parallel_size,
            gpu_memory_utilization=settings.gpu_memory_utilization,
            max_model_len=settings.max_model_len,
            trust_remote_code=True,
        )
        
        engine = AsyncLLMEngine.from_engine_args(engine_args)
        logger.info("vLLM engine initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize vLLM engine: {e}")
        raise
    
    
    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down vLLM service...")


# Create FastAPI application
app = FastAPI(
    title="vLLM Text Generation Service",
    description="High-throughput LLM inference service using vLLM",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": "vLLM Text Generation Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the service status and model information.
    """
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="vLLM engine not initialized"
        )
    
    return HealthResponse(
        status="healthy",
        model=settings.model_name,
        vllm_version=vllm_version
    )


@app.post(
    "/generate_text",
    response_model=GenerateTextResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse}
    },
    tags=["Text Generation"]
)
async def generate_text(request: GenerateTextRequest):
    """
    Generate text using the loaded LLM model.
    
    This endpoint accepts a prompt and generation parameters, then returns
    the generated text along with metadata.
    
    Args:
        request: GenerateTextRequest containing prompt and generation parameters
        
    Returns:
        GenerateTextResponse with generated text and metadata
        
    Raises:
        HTTPException: If generation fails or service is unavailable
    """
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="vLLM engine not initialized"
        )
    
    if request.stream:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Streaming is not yet implemented. Set stream=false"
        )
    
    try:
        # Create sampling parameters
        sampling_params = SamplingParams(
            max_tokens=request.max_tokens or settings.default_max_tokens,
            temperature=request.temperature if request.temperature is not None else settings.default_temperature,
            top_p=request.top_p if request.top_p is not None else settings.default_top_p,
            top_k=request.top_k if request.top_k is not None else -1,
            frequency_penalty=request.frequency_penalty or 0.0,
            presence_penalty=request.presence_penalty or 0.0,
            stop=request.stop,
        )
        
        logger.info(f"Generating text for prompt: {request.prompt[:50]}...")
        
        # Generate text using vLLM
        request_id = f"req_{asyncio.current_task().get_name()}"
        results = []
        
        async for result in engine.generate(
            request.prompt,
            sampling_params,
            request_id=request_id
        ):
            results.append(result)
        
        # Get the final result
        final_result = results[-1]
        output = final_result.outputs[0]
        
        # Calculate token usage
        prompt_tokens = len(final_result.prompt_token_ids)
        completion_tokens = len(output.token_ids)
        
        logger.info(f"Generation complete. Tokens: {prompt_tokens} + {completion_tokens}")
        
        return GenerateTextResponse(
            text=output.text,
            prompt=request.prompt,
            model=settings.model_name,
            finish_reason=output.finish_reason,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}"
        )


@app.get("/model_info", tags=["Information"])
async def model_info():
    """
    Get information about the loaded model.
    
    Returns model configuration and settings.
    """
    return {
        "model_name": settings.model_name,
        "model_revision": settings.model_revision,
        "tensor_parallel_size": settings.tensor_parallel_size,
        "gpu_memory_utilization": settings.gpu_memory_utilization,
        "max_model_len": settings.max_model_len,
        "default_max_tokens": settings.default_max_tokens,
        "default_temperature": settings.default_temperature,
        "default_top_p": settings.default_top_p
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.service_host,
        port=settings.service_port,
        log_level=settings.log_level.lower(),
        workers=1,
        reload=False
    )
