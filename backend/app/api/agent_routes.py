
"""
Advanced agent routing with CoordinatorAgent
"""
import logging
from typing import Generator
from fastapi import APIRouter, HTTPException, status, Depends

from app.agents.coordinator import CoordinatorAgent
from app.agents.injury_agent import InjuryAgent
from app.agents.db_connection import DatabaseConnection
from app.services.vllm_client import llm_client
from app.services.retriever_client import retriever_client
from app.agents.verifier_agent import CitationVerifierLLM
from app.core.config import settings

from app.models.schemas import (
    InjuryAnalysisRequest,
    InjuryAnalysisResponse,
    InjuryReportRequest,
    InjuryReportResponse,
    WeeklyReportRequest,
    WeeklyReportResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

def get_db_reader() -> Generator[DatabaseConnection, None, None]:
    """
    Dependency to get database reader connection
    """
    db = DatabaseConnection(use_writer=False)
    try:
        yield db
    finally:
        db.close()

def get_db_writer() -> Generator[DatabaseConnection, None, None]:
    """
    Dependency to get database writer connection
    """
    db = DatabaseConnection(use_writer=True)
    try:
        yield db
    finally:
        db.close()

# Singleton instances
_coordinator_instance = None
_injury_agent_instance = None

def get_coordinator() -> CoordinatorAgent:
    """
    Get singleton CoordinatorAgent instance.
    Initialized once, reused for all requests.
    """
    global _coordinator_instance
    if _coordinator_instance is None:
        # Initialize without DB - we'll inject per request
        _coordinator_instance = CoordinatorAgent(llm_client, retriever_client)
        logger.info("✓ Initialized singleton CoordinatorAgent with all child agents")
    return _coordinator_instance

def get_injury_agent() -> InjuryAgent:
    """Get singleton InjuryAgent instance"""
    global _injury_agent_instance
    if _injury_agent_instance is None:
        verifier = CitationVerifierLLM(llm_client)
        _injury_agent_instance = InjuryAgent(llm_client, retriever_client, verifier)
        logger.info("✓ Initialized singleton InjuryAgent")
    return _injury_agent_instance

# ========== COORDINATOR ROUTES ==========

@router.post("/weekly-report", response_model=WeeklyReportResponse)
async def generate_weekly_report(
    request: WeeklyReportRequest,
    coordinator: CoordinatorAgent = Depends(get_coordinator),
):
    """
    Generate comprehensive weekly injury report for all starting players
    
    This uses the CoordinatorAgent to orchestrate injury analysis across all players.
    """
    try:
        logger.info(f"Generating weekly report for week {request.week_number}")

        report = await coordinator.generate_weekly_report(request.week_number)

        return {
            "week": request.week_number,
            "report": report,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly report: {str(e)}"
        )

# ========== INJURY AGENT ROUTES ==========

@router.post("/injury/analyze", response_model=InjuryAnalysisResponse)
async def analyze_injury(
    request: InjuryAnalysisRequest,
    injury_agent: InjuryAgent = Depends(get_injury_agent)
):
    """
    Analyze injury for a single player
    
    Returns detailed injury analysis for one player.
    """
    try:
        query = f"{request.player_name} injury status week {request.week_number}"
        analysis = await injury_agent.analyze_injury(query)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No injury information found for {request.player_name}"
            )
        
        return {
            "player": request.player_name,
            "week": request.week_number,
            "analysis": analysis['content'],
            "verification": analysis['verification'],
            "retrieved_documents": analysis['retrieved_documents'],
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing injury for {request.player_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze injury: {str(e)}"
        )

@router.post("/injury/report", response_model=InjuryReportResponse)
async def generate_injury_report(
    request: InjuryReportRequest,
    injury_agent: InjuryAgent = Depends(get_injury_agent)
):
    """
    Generate injury report for custom list of players
    
    Allows generating a report for any subset of players, not just starters.
    """
    try:
        logger.info(f"Generating injury report for {len(request.players)} players")
        report = await injury_agent.generate_team_injury_report(request.players, request.week_number)

        return {
            "week": request.week_number,
            "players": request.players,
            "report": report,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating injury report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate injury report: {str(e)}"
        )


# ========== DATABASE ROUTES ==========

@router.get("/weekly-report/{week_number}")
async def get_past_report(week_number: int, coordinator: CoordinatorAgent = Depends(get_coordinator)):
    """
    Retrieve a previously generated weekly report
    """
    try:
        # TODO: Retrieve from S3

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
async def check_db_health(db: DatabaseConnection = Depends(get_db_reader)):
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