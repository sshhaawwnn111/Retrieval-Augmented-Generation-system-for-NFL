"""
FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api import llm_routes
from app.api import s3_routes

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
    
    yield
    
    # Shutdown
    logger.info("Shutting down RavensRotoWire Backend...")


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
    """Health check endpoint for ECS/ALB"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "vllm_service": settings.VLLM_SERVICE_URL or "not_configured"
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
