"""
Self-hosted vLLM Service Client
"""
import json
import logging
from typing import Dict, Any, Optional, List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)
 
 

class VLLMClient:
    """
    Client for invoking self-hosted vLLM service for LLM inference.
    """
    
    def __init__(self):
        """Initialize vLLM client"""
        self.base_url = settings.VLLM_SERVICE_URL  # e.g., "http://localhost:8001"
        self.timeout = settings.VLLM_TIMEOUT or 120.0
        self.max_retries = settings.VLLM_MAX_RETRIES or 3
        
        # Create async HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        
        logger.info(f"Initialized vLLM client for service: {self.base_url}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check vLLM service health
        
        Returns:
            Dict containing health status
        """
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Health check failed: {str(e)}")
            raise Exception(f"vLLM service health check failed: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Top-p sampling parameter
            stop_sequences: List of sequences to stop generation
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text string
        """
        if system_prompt:
            formatted_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            formatted_prompt = prompt
        
        response = await self.invoke_endpoint(
            prompt=formatted_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop_sequences=stop_sequences,
            **kwargs
        )
        
        return response["text"]
    
    async def invoke_endpoint(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Invoke vLLM service endpoint with a prompt
        
        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Top-p sampling parameter
            stop_sequences: List of sequences to stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict containing the generated text and metadata
        """
        # Prepare request payload
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens or settings.LLM_MAX_TOKENS or 512,
            "temperature": temperature if temperature is not None else (settings.LLM_TEMPERATURE or 0.7),
            "top_p": top_p if top_p is not None else (settings.LLM_TOP_P or 0.95),
        }
        
        if stop_sequences:
            payload["stop"] = stop_sequences
        
        # Add any additional parameters
        payload.update(kwargs)
        
        try:
            logger.info(f"Invoking vLLM service at: {self.base_url}/generate_text")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = await self.client.post(
                "/generate_text",
                json=payload
            )
            
            response.raise_for_status()
            
            # Parse response
            response_body = response.json()
            logger.info("Successfully received response from vLLM service")
            logger.debug(f"Response: {json.dumps(response_body, indent=2)}")
            
            return self._parse_response(response_body)
            
        except httpx.HTTPStatusError as e:
            error_message = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"vLLM service error: {error_message}")
            raise Exception(f"vLLM invocation failed: {error_message}")
        except httpx.RequestError as e:
            logger.error(f"Request error to vLLM service: {str(e)}")
            raise Exception(f"Failed to connect to vLLM service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error invoking vLLM: {str(e)}")
            raise
    
    def _parse_response(self, response_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse response from vLLM service
        
        Expected response format from your service:
        {
            "text": "...",
            "prompt": "...",
            "model": "...",
            "finish_reason": "...",
            "usage": {...}
        }
        """
        if "text" in response_body:
            return {
                "text": response_body["text"],
                "model": response_body.get("model", "unknown"),
                "usage": response_body.get("usage", {}),
                "prompt": response_body.get("prompt", ""),
                "raw_response": response_body
            }
        else:
            logger.warning(f"Unknown response format: {response_body}")
            return {
                "generated_text": str(response_body),
                "model": "unknown",
                "usage": {},
                "raw_response": response_body
            }
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dict containing model information
        """
        try:
            response = await self.client.get("/model_info")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get model info: {str(e)}")
            raise Exception(f"Failed to get model info: {str(e)}")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        logger.info("vLLM client closed")


# Global instance
llm_client = VLLMClient()