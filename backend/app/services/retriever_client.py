import logging
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class RetrieverClient:
    """Client for interacting with the retriever service"""
    
    def __init__(self):
        self.base_url = settings.RETRIEVER_SERVICE_URL
        self.timeout = 60.0
    
    async def retrieve_and_rerank(
        self, 
        query: str, 
        k: int = 10, 
        top_n: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and rerank documents relevant to the query
        
        Args:
            query: Search query
            k: Number of documents to retrieve initially
            top_n: Number of top documents to return after reranking
            
        Returns:
            List of reranked documents with metadata
        """
        try:
            logger.info(f"Retrieving documents at {self.base_url}/retrieve_and_rerank")
            
            payload = {
                "query": query,
                "k": k,
                "top_n": top_n
            }
            
            if filters:
                payload["filters"] = filters

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/retrieve_and_rerank",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data.get("documents", [])
                
        except httpx.TimeoutException:
            logger.error(f"Timeout calling retriever service for query: {query}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling retriever service: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling retriever service: {e}")
            raise


# Create singleton instance
retriever_client = RetrieverClient()