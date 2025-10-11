"""
API routes for LLM operations
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.schemas import (
    LLMGenerateRequest,
    LLMGenerateResponse,
    Text2SQLRequest,
    Text2SQLResponse,
    RetrievalRequest,
    RetrievalResponse,
    ReportGenerationRequest,
    ReportGenerationResponse
)
# from app.services.sagemaker_client import llm_client
from app.services.vllm_client import llm_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=LLMGenerateResponse)
async def generate_text(request: LLMGenerateRequest):
    """
    Generate text using the LLM
    
    This endpoint directly invokes the SageMaker LLM endpoint with the provided prompt.
    """
    try:
        logger.info(f"Generating text for prompt: {request.prompt[:100]}...")
        
        generated_text = await llm_client.generate_text(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop_sequences=request.stop_sequences
        )
        
        return LLMGenerateResponse(
            generated_text=generated_text,
            model="sagemaker-endpoint",
            usage={}
        )
        
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate text: {str(e)}"
        )


@router.post("/text2sql", response_model=Text2SQLResponse)
async def text_to_sql(request: Text2SQLRequest):
    """
    Convert natural language question to SQL query
    
    This endpoint uses the LLM to generate SQL queries from natural language questions.
    It can incorporate database schema context and few-shot examples.
    """
    try:
        logger.info(f"Converting question to SQL: {request.question}")
        
        # Build prompt for text-to-SQL
        prompt = _build_text2sql_prompt(
            question=request.question,
            schema_context=request.schema_context,
            few_shot_examples=request.few_shot_examples
        )
        
        # Generate SQL using LLM
        generated_text = await llm_client.generate_text(
            prompt=prompt,
            system_prompt="You are an expert SQL developer. Generate SQL queries based on natural language questions.",
            temperature=0.1,  # Lower temperature for more deterministic SQL
            stop_sequences=["</sql>", "\n\n"]
        )
        
        # Extract SQL from response
        sql_query = _extract_sql(generated_text)
        
        return Text2SQLResponse(
            sql_query=sql_query,
            confidence=None,  # TODO: Add confidence scoring
            explanation=generated_text
        )
        
    except Exception as e:
        logger.error(f"Error converting text to SQL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SQL: {str(e)}"
        )


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_context(request: RetrievalRequest):
    """
    Retrieve relevant context/documents for a query
    
    This endpoint performs semantic search over stored documents/embeddings
    to retrieve relevant context for RAG (Retrieval-Augmented Generation).
    """
    try:
        logger.info(f"Retrieving context for query: {request.query}")
        
        # TODO: Implement vector search using pgvector in Aurora PostgreSQL
        # For now, return placeholder
        
        results = [
            {
                "content": "Placeholder document 1",
                "score": 0.95,
                "metadata": {"source": "database"}
            }
        ]
        
        return RetrievalResponse(
            results=results,
            total_count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve context: {str(e)}"
        )


@router.post("/generate-report", response_model=ReportGenerationResponse)
async def generate_report(request: ReportGenerationRequest):
    """
    Generate a report from query results
    
    This endpoint takes SQL query results and generates a natural language report
    using the LLM.
    """
    try:
        logger.info(f"Generating report of type: {request.report_type}")
        
        # Build prompt for report generation
        prompt = _build_report_prompt(
            query_results=request.query_results,
            report_type=request.report_type,
            additional_context=request.additional_context
        )
        
        # Generate report using LLM
        report = await llm_client.generate_text(
            prompt=prompt,
            system_prompt="You are a professional sports analyst writing reports about NFL data.",
            temperature=0.7,  # Higher temperature for more creative writing
            max_tokens=2048
        )
        
        # TODO: Save to S3 if needed
        
        return ReportGenerationResponse(
            report=report,
            report_type=request.report_type,
            s3_url=None
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


def _build_text2sql_prompt(
    question: str,
    schema_context: str = None,
    few_shot_examples: list = None
) -> str:
    """Build prompt for text-to-SQL generation"""
    prompt_parts = []
    
    if schema_context:
        prompt_parts.append(f"Database Schema:\n{schema_context}\n")
    
    if few_shot_examples:
        prompt_parts.append("Examples:")
        for example in few_shot_examples:
            prompt_parts.append(f"Q: {example.get('question')}")
            prompt_parts.append(f"SQL: {example.get('sql')}\n")
    
    prompt_parts.append(f"Question: {question}")
    prompt_parts.append("SQL:")
    
    return "\n".join(prompt_parts)


def _extract_sql(generated_text: str) -> str:
    """Extract SQL query from generated text"""
    # Remove markdown code blocks if present
    text = generated_text.strip()
    
    if "```sql" in text:
        start = text.find("```sql") + 6
        end = text.find("```", start)
        return text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        return text[start:end].strip()
    
    # Look for SELECT, INSERT, UPDATE, DELETE statements
    for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE", "WITH"]:
        if keyword in text.upper():
            lines = text.split("\n")
            sql_lines = []
            found_start = False
            for line in lines:
                if keyword in line.upper():
                    found_start = True
                if found_start:
                    sql_lines.append(line)
                    if line.strip().endswith(";"):
                        break
            return "\n".join(sql_lines).strip()
    
    return text.strip()


def _build_report_prompt(
    query_results: Dict[str, Any],
    report_type: str,
    additional_context: str = None
) -> str:
    """Build prompt for report generation"""
    prompt_parts = []
    
    prompt_parts.append(f"Generate a {report_type} report based on the following data:")
    prompt_parts.append(f"\nData:\n{query_results}\n")
    
    if additional_context:
        prompt_parts.append(f"Additional Context:\n{additional_context}\n")
    
    prompt_parts.append("Please provide a well-structured, professional report:")
    
    return "\n".join(prompt_parts)
