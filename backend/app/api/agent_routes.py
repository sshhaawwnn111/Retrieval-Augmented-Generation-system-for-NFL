
"""
Advanced agent routing with CoordinatorAgent
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends

from agents.coordinator import CoordinatorAgent
from agents.db_connection import DatabaseConnection
from app.services.vllm_client import llm_client
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

def get_db(use_writer: bool = False):
    """
    Dependency to get database connection
    
    Args:
        use_writer: If True, returns writer connection for write operations
    """
    db = DatabaseConnection(use_writer=use_writer)
    try:
        yield db
    finally:
        db.close()


@router.post("/weekly-report")
async def generate_weekly_report(week_number: int, db: DatabaseConnection = Depends(get_db)):
    """
    Generate comprehensive weekly injury report for all starting players
    
    This uses the CoordinatorAgent to orchestrate injury analysis across all players.
    """
    try:
        logger.info(f"Generating weekly report for week {week_number}")
        
        coordinator = CoordinatorAgent(llm_client, db)
        report = coordinator.generate_weekly_report(week_number)
        
        return {
            "week": week_number,
            "report": report,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly report: {str(e)}"
        )


@router.get("/weekly-report/{week_number}")
async def get_past_report(week_number: int, db: DatabaseConnection = Depends(get_db)):
    """
    Retrieve a previously generated weekly report
    """
    try:
        coordinator = CoordinatorAgent(llm_client, db)
        report = coordinator.get_past_report(week_number)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No report found for week {week_number}"
            )
        
        return {
            "week": week_number,
            "report": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving past report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}"
        )


@router.get("/health/db")
async def check_db_health(db: DatabaseConnection = Depends(get_db)):
    """
    Check database connection health
    """
    try:
        result = db.execute_query("SELECT version(), current_database(), current_user")
        version, database, user = result[0]
        
        return {
            "status": "healthy",
            "database": database,
            "user": user,
            "postgres_version": version
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )