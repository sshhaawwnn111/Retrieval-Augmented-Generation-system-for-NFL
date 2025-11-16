"""
FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api import llm_routes, agent_routes, s3_routes
from agents.db_connection import DatabaseConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting RavensRotoWire Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AWS Region: {settings.AWS_REGION}")
    
    # Initialize database connection pools
    try:
        DatabaseConnection.initialize_pools(
            dbname=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            writer_host=settings.DATABASE_HOST,  # Cluster/Writer endpoint
            reader_host=settings.DATABASE_READER_HOST,  # Reader endpoint
            port=settings.DATABASE_PORT,
            min_conn=2,
            max_conn=10
        )
        logger.info("Database connection pools initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pools: {e}")
        raise

    yield
    
    # Shutdown
    logger.info("Shutting down RavensRotoWire Backend...")
    try:
        DatabaseConnection.close_all_connections()
        logger.info("Database connection pools closed successfully")
    except Exception as e:
        logger.error(f"Error closing database pools: {e}")


# Create FastAPI application
app = FastAPI(
    title="RavensRotoWire API",
    description="Backend API for RavensRotoWire - Text-to-SQL with LLM",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RavensRotoWire API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for ECS/ALB with full configuration"""
    return {
        "status": "healthy",
        
        # Environment
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        
        # AWS Configuration
        "aws": {
            "region": settings.AWS_REGION,
            "access_key_configured": bool(settings.AWS_ACCESS_KEY_ID),
            "secret_key_configured": bool(settings.AWS_SECRET_ACCESS_KEY),
        },
        
        # SageMaker
        "sagemaker": {
            "endpoint_name": settings.SAGEMAKER_ENDPOINT_NAME or "not_configured",
            "timeout": settings.SAGEMAKER_TIMEOUT,
            "max_retries": settings.SAGEMAKER_MAX_RETRIES,
        },
        
        # vLLM Service
        "vllm": {
            "service_url": settings.VLLM_SERVICE_URL,
            "model_name": settings.VLLM_MODEL_NAME,
            "timeout": settings.VLLM_TIMEOUT,
            "max_retries": settings.VLLM_MAX_RETRIES,
        },
        
        # LLM Settings
        "llm": {
            "model_type": settings.LLM_MODEL_TYPE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "temperature": settings.LLM_TEMPERATURE,
            "top_p": settings.LLM_TOP_P,
        },
        
        # Database
        "database": {
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
            "name": settings.DATABASE_NAME,
            "user": settings.DATABASE_USER,
            "password_configured": bool(settings.DATABASE_PASSWORD),
            "ssl_enabled": settings.DATABASE_SSL,
            "reader_host": settings.DATABASE_READER_HOST or "not_configured",
        },
        
        # S3
        "s3": {
            "region": settings.S3_REGION,
            "bucket_name": settings.S3_BUCKET_NAME,
            "reports_prefix": settings.S3_REPORTS_PREFIX,
            "raw_data_prefix": settings.S3_RAW_DATA_PREFIX,
            "embeddings_prefix": settings.S3_EMBEDDINGS_PREFIX,
        },
        
        # Reranker
        "reranker": {
            "service_url": settings.RERANKER_SERVICE_URL or "not_configured",
        },
        
        # CloudWatch
        "cloudwatch": {
            "log_group": settings.CLOUDWATCH_LOG_GROUP,
            "log_stream": settings.CLOUDWATCH_LOG_STREAM,
        },
        
        # Vector Search
        "vector_search": {
            "embedding_dimension": settings.EMBEDDING_DIMENSION,
        },
        
        # CORS
        "cors_origins_count": len(settings.CORS_ORIGINS),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Add checks for dependencies (DB, SageMaker, etc.)
    try:
        # TODO: Add actual readiness checks
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )



# Include API routes
app.include_router(llm_routes.router, prefix="/api/v1", tags=["LLM"])
app.include_router(agent_routes.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(s3_routes.router, prefix="/api/v1/s3", tags=["S3"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
