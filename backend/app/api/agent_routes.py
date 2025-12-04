"""
Advanced agent routing with CoordinatorAgent
"""
import logging
from typing import Generator
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta

from app.agents.coordinator import CoordinatorAgent
from app.agents.injury_agent import InjuryAgent
from app.agents.waiver_agent import WaiverAgent
from app.agents.news_agent import NewsAgent
from app.agents.performance_agent import PerformanceAgent
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
from app.models.schemas import GenericAnalysisRequest, GenericAnalysisResponse

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
_news_agent_instance = None
_performance_agent_instance = None
_waiver_agent_instance = None


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

def get_news_agent() -> NewsAgent:
    global _news_agent_instance
    if _news_agent_instance is None:
        verifier = CitationVerifierLLM(llm_client)
        _news_agent_instance = NewsAgent(llm_client, retriever_client, verifier)
        logger.info("✓ Initialized singleton NewsAgent")
    return _news_agent_instance


def get_performance_agent() -> PerformanceAgent:
    global _performance_agent_instance
    if _performance_agent_instance is None:
        verifier = CitationVerifierLLM(llm_client)
        _performance_agent_instance = PerformanceAgent(llm_client, retriever_client, verifier)
        logger.info("✓ Initialized singleton PerformanceAgent")
    return _performance_agent_instance


def get_waiver_agent() -> WaiverAgent:
    global _waiver_agent_instance
    if _waiver_agent_instance is None:
        verifier = CitationVerifierLLM(llm_client)
        _waiver_agent_instance = WaiverAgent(llm_client, retriever_client, verifier)
        logger.info("✓ Initialized singleton WaiverAgent")
    return _waiver_agent_instance

def get_date_range(date: str) -> int:
    start_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=180)).strftime("%Y-%m-%d")
    end_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
    return start_date, end_date

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
        logger.info(f"Generating weekly report for week {request.date}")

        report = await coordinator.generate_weekly_report(request.date)

        return {
            "date": request.date,
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
        start_date, end_date = get_date_range(request.date)

        query = f"{request.player_name} injury status date {request.date}"
        analysis = await injury_agent.analyze_injury(
            query, 
            filters={"player_name": request.player_name, 
                     "start_date": start_date, 
                     "end_date": end_date}
        )
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No injury information found for {request.player_name}"
            )
        
        return {
            "player": request.player_name,
            "date": request.date,
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
        report = await injury_agent.generate_team_injury_report(request.players, request.date)

        return {
            "date": request.date,
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


@router.post("/news/analyze", response_model=GenericAnalysisResponse)
async def analyze_news(
    request: GenericAnalysisRequest,
    news_agent: NewsAgent = Depends(get_news_agent)
):
    try:
        result = await news_agent.analyze_news(request.query, k=request.k, top_n=request.top_n)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No news data found")
        return {"content": result["content"], "verification": result.get("verification", []), "retrieved_documents": result.get("retrieved_documents", []), "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing news: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/performance/analyze", response_model=GenericAnalysisResponse)
async def analyze_performance(
    request: GenericAnalysisRequest,
    performance_agent: PerformanceAgent = Depends(get_performance_agent)
):
    try:
        result = await performance_agent.analyze_performance(request.query, k=request.k, top_n=request.top_n)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No performance data found")
        return {"content": result["content"], "verification": result.get("verification", []), "retrieved_documents": result.get("retrieved_documents", []), "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing performance: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/waiver/analyze", response_model=GenericAnalysisResponse)
async def analyze_waiver(
    request: GenericAnalysisRequest,
    waiver_agent: WaiverAgent = Depends(get_waiver_agent)
):
    try:
        result = await waiver_agent.analyze_waiver(request.query, k=request.k, top_n=request.top_n)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No waiver data found")
        return {"content": result["content"], "verification": result.get("verification", []), "retrieved_documents": result.get("retrieved_documents", []), "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing waiver: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========== DATABASE ROUTES ==========

@router.get("/weekly-report/{date}")
async def get_past_report(date: str, coordinator: CoordinatorAgent = Depends(get_coordinator)):
    """
    Retrieve a previously generated weekly report
    """
    try:
        # TODO: Retrieve from S3

        report = coordinator.get_past_report(date)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No report found for date {date}"
            )
        
        return {
            "date": date,
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