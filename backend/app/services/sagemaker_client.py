"""
AWS SageMaker LLM Service Client
"""
import json
import logging
from typing import Dict, Any, Optional, List

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class SageMakerLLMClient:
    """
    Client for invoking AWS SageMaker endpoints for LLM inference.
    Supports vLLM and Ollama deployments.
    """
    
    def __init__(self):
        """Initialize SageMaker runtime client"""
        self.endpoint_name = settings.SAGEMAKER_ENDPOINT_NAME
        
        # Configure boto3 client with retry settings
        config = Config(
            region_name=settings.AWS_REGION,
            retries={
                'max_attempts': settings.SAGEMAKER_MAX_RETRIES,
                'mode': 'adaptive'
            },
            read_timeout=settings.SAGEMAKER_TIMEOUT,
            connect_timeout=30
        )
        
        self.client = boto3.client('sagemaker-runtime', config=config)
        logger.info(f"Initialized SageMaker client for endpoint: {self.endpoint_name}")
    
    def invoke_endpoint(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Invoke SageMaker endpoint with a prompt
        
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
        if not self.endpoint_name:
            raise ValueError("SAGEMAKER_ENDPOINT_NAME not configured")
        
        # Prepare request payload based on model type
        payload = self._prepare_payload(
            prompt=prompt,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
            temperature=temperature or settings.LLM_TEMPERATURE,
            top_p=top_p or settings.LLM_TOP_P,
            stop_sequences=stop_sequences,
            **kwargs
        )
        
        try:
            logger.info(f"Invoking endpoint: {self.endpoint_name}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = self.client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload),
                Accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['Body'].read().decode('utf-8'))
            logger.info("Successfully received response from SageMaker endpoint")
            logger.debug(f"Response: {json.dumps(response_body, indent=2)}")
            
            return self._parse_response(response_body)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"SageMaker ClientError: {error_code} - {error_message}")
            raise Exception(f"SageMaker invocation failed: {error_message}")
        except Exception as e:
            logger.error(f"Unexpected error invoking SageMaker: {str(e)}")
            raise
    
    def _prepare_payload(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        stop_sequences: Optional[List[str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare payload for SageMaker endpoint based on model type
        """
        if settings.LLM_MODEL_TYPE == "vllm":
            # vLLM format (OpenAI-compatible)
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": False
            }
            if stop_sequences:
                payload["stop"] = stop_sequences
                
        elif settings.LLM_MODEL_TYPE == "ollama":
            # Ollama format
            payload = {
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                }
            }
            if stop_sequences:
                payload["options"]["stop"] = stop_sequences
        else:
            # Generic format
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "do_sample": temperature > 0,
                }
            }
            if stop_sequences:
                payload["parameters"]["stop_sequences"] = stop_sequences
        
        # Add any additional parameters
        payload.update(kwargs)
        
        return payload
    
    def _parse_response(self, response_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse response from SageMaker endpoint
        """
        # Handle vLLM response format
        if "choices" in response_body:
            return {
                "generated_text": response_body["choices"][0]["text"],
                "model": response_body.get("model", "unknown"),
                "usage": response_body.get("usage", {}),
                "raw_response": response_body
            }
        
        # Handle Ollama response format
        elif "response" in response_body:
            return {
                "generated_text": response_body["response"],
                "model": response_body.get("model", "unknown"),
                "usage": {
                    "total_duration": response_body.get("total_duration", 0),
                    "load_duration": response_body.get("load_duration", 0),
                    "eval_count": response_body.get("eval_count", 0)
                },
                "raw_response": response_body
            }
        
        # Handle generic HuggingFace format
        elif "generated_text" in response_body:
            return {
                "generated_text": response_body["generated_text"],
                "model": "unknown",
                "usage": {},
                "raw_response": response_body
            }
        
        # Handle list response (batch)
        elif isinstance(response_body, list) and len(response_body) > 0:
            return {
                "generated_text": response_body[0].get("generated_text", ""),
                "model": "unknown",
                "usage": {},
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
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt (async wrapper)
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text string
        """
        # Combine system and user prompts if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.invoke_endpoint(full_prompt, **kwargs)
        return response["generated_text"]


# Global instance
llm_client = SageMakerLLMClient()
