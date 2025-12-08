"""
FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.secrets import get_database_credentials
from app.api import llm_routes, agent_routes, s3_routes
from app.agents.db_connection import DatabaseConnection

from fastapi.middleware.cors import CORSMiddleware


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Filter out security scan noise
class SecurityScanFilter(logging.Filter):
    """Filter out known security scanning patterns"""
    SCAN_PATTERNS = [
        'phpunit',
        'eval-stdin.php',
        'vendor/phpunit',
        'config-create',
        '/containers/json',
        'invokefunction',
        'allow_url_include',
    ]
    
    def filter(self, record):
        # Only filter INFO level messages from uvicorn.access
        if record.name == "uvicorn.access" and record.levelno == logging.INFO:
            message = record.getMessage()
            # Filter out security scan attempts
            return not any(pattern in message for pattern in self.SCAN_PATTERNS)
        return True

access_logger = logging.getLogger("uvicorn.access")
access_logger.addFilter(SecurityScanFilter())

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting RavensRotoWire Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AWS Region: {settings.AWS_REGION}")
    
    # Get database credentials - start with settings defaults
    db_password = settings.DATABASE_PASSWORD
    db_user = settings.DATABASE_USER
    db_host = settings.DATABASE_HOST
    db_reader_host = settings.DATABASE_READER_HOST
    
    if settings.USE_SECRETS_MANAGER:
        try:
            logger.info(f"Retrieving database credentials from Secrets Manager: {settings.DATABASE_SECRET_NAME}")
            credentials = get_database_credentials(
                secret_name=settings.DATABASE_SECRET_NAME,
                region=settings.AWS_REGION
            )
            
            # RDS-managed secrets only contain username and password
            db_user = credentials.get('username', db_user)
            db_password = credentials.get('password', db_password)
            
            logger.info(f"Successfully retrieved database credentials for user: {db_user}")
            
        except Exception as e:
            logger.error(f"Failed to retrieve secrets from Secrets Manager: {e}")
            logger.warning("Falling back to environment variables")

    # Initialize database connection pools
    try:
        DatabaseConnection.initialize_pools(
            dbname=settings.DATABASE_NAME,
            user=db_user,
            password=db_password,
            writer_host=db_host,  # Cluster/Writer endpoint
            reader_host=db_reader_host,  # Reader endpoint
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
        
        # vLLM Service
        "vllm": {
            "llm service_url": settings.VLLM_SERVICE_URL,
            "retriever service_url": settings.RETRIEVER_SERVICE_URL,
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
            "ssl_enabled": settings.DATABASE_SSL,
            "reader_host": settings.DATABASE_READER_HOST or "not_configured",
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
