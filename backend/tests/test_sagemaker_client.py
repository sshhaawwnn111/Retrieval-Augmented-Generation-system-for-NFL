"""
Unit tests for SageMaker LLM Client
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from app.services.sagemaker_client import SageMakerLLMClient


@pytest.fixture
def mock_boto_client():
    """Mock boto3 SageMaker runtime client"""
    with patch('boto3.client') as mock_client:
        yield mock_client


@pytest.fixture
def llm_client(mock_boto_client):
    """Create LLM client with mocked boto3"""
    with patch('app.services.sagemaker_client.settings') as mock_settings:
        mock_settings.SAGEMAKER_ENDPOINT_NAME = "test-endpoint"
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.SAGEMAKER_MAX_RETRIES = 3
        mock_settings.SAGEMAKER_TIMEOUT = 120
        mock_settings.LLM_MODEL_TYPE = "vllm"
        mock_settings.LLM_MAX_TOKENS = 2048
        mock_settings.LLM_TEMPERATURE = 0.1
        mock_settings.LLM_TOP_P = 0.95
        
        client = SageMakerLLMClient()
        return client


def test_prepare_payload_vllm(llm_client):
    """Test payload preparation for vLLM format"""
    with patch('app.services.sagemaker_client.settings') as mock_settings:
        mock_settings.LLM_MODEL_TYPE = "vllm"
        
        payload = llm_client._prepare_payload(
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.5,
            top_p=0.9,
            stop_sequences=["###"]
        )
        
        assert payload["prompt"] == "Test prompt"
        assert payload["max_tokens"] == 100
        assert payload["temperature"] == 0.5
        assert payload["top_p"] == 0.9
        assert payload["stop"] == ["###"]


def test_prepare_payload_ollama(llm_client):
    """Test payload preparation for Ollama format"""
    with patch('app.services.sagemaker_client.settings') as mock_settings:
        mock_settings.LLM_MODEL_TYPE = "ollama"
        
        payload = llm_client._prepare_payload(
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.5,
            top_p=0.9,
            stop_sequences=None
        )
        
        assert payload["prompt"] == "Test prompt"
        assert payload["options"]["num_predict"] == 100
        assert payload["options"]["temperature"] == 0.5
        assert payload["options"]["top_p"] == 0.9


def test_parse_response_vllm(llm_client):
    """Test response parsing for vLLM format"""
    response_body = {
        "choices": [
            {
                "text": "Generated text",
                "finish_reason": "stop"
            }
        ],
        "model": "test-model",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
    
    parsed = llm_client._parse_response(response_body)
    
    assert parsed["generated_text"] == "Generated text"
    assert parsed["model"] == "test-model"
    assert parsed["usage"]["total_tokens"] == 30


def test_parse_response_ollama(llm_client):
    """Test response parsing for Ollama format"""
    response_body = {
        "response": "Generated text from Ollama",
        "model": "llama2",
        "total_duration": 1234567,
        "eval_count": 50
    }
    
    parsed = llm_client._parse_response(response_body)
    
    assert parsed["generated_text"] == "Generated text from Ollama"
    assert parsed["model"] == "llama2"
    assert parsed["usage"]["eval_count"] == 50


@pytest.mark.asyncio
async def test_generate_text(llm_client):
    """Test text generation with system prompt"""
    mock_response = {
        "generated_text": "Test response",
        "model": "test-model",
        "usage": {}
    }
    
    with patch.object(llm_client, 'invoke_endpoint', return_value=mock_response):
        result = await llm_client.generate_text(
            prompt="Test prompt",
            system_prompt="You are a helpful assistant"
        )
        
        assert result == "Test response"


def test_invoke_endpoint_success(llm_client):
    """Test successful endpoint invocation"""
    mock_client = Mock()
    mock_response = {
        'Body': MagicMock(read=lambda: json.dumps({
            "choices": [{"text": "Success"}],
            "model": "test"
        }).encode('utf-8'))
    }
    mock_client.invoke_endpoint.return_value = mock_response
    llm_client.client = mock_client
    
    result = llm_client.invoke_endpoint(prompt="Test")
    
    assert result["generated_text"] == "Success"
    mock_client.invoke_endpoint.assert_called_once()


def test_invoke_endpoint_no_endpoint_name():
    """Test error when endpoint name not configured"""
    with patch('app.services.sagemaker_client.settings') as mock_settings:
        mock_settings.SAGEMAKER_ENDPOINT_NAME = None
        client = SageMakerLLMClient()
        
        with pytest.raises(ValueError, match="SAGEMAKER_ENDPOINT_NAME not configured"):
            client.invoke_endpoint(prompt="Test")
