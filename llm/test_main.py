"""
Unit tests for vLLM service.

Note: These tests mock the vLLM engine to avoid requiring GPU resources.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_engine():
    """Mock vLLM engine."""
    mock = AsyncMock()
    
    # Mock the generate method to return a result
    async def mock_generate(prompt, sampling_params, request_id):
        # Create a mock result
        mock_output = Mock()
        mock_output.text = "This is a generated response."
        mock_output.token_ids = [1, 2, 3, 4, 5]
        mock_output.finish_reason = "stop"
        
        mock_result = Mock()
        mock_result.prompt_token_ids = [10, 20, 30]
        mock_result.outputs = [mock_output]
        
        yield mock_result
    
    mock.generate = mock_generate
    return mock


@pytest.fixture
def client(mock_engine):
    """Create test client with mocked engine."""
    with patch('main.engine', mock_engine):
        # Import after patching to avoid initialization issues
        from main import app
        with TestClient(app) as test_client:
            yield test_client


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "vLLM Text Generation Service"
    assert data["status"] == "running"


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model" in data
    assert "vllm_version" in data


def test_model_info_endpoint(client):
    """Test model info endpoint."""
    response = client.get("/model_info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "tensor_parallel_size" in data
    assert "max_model_len" in data


def test_generate_text_basic(client):
    """Test basic text generation."""
    request_data = {
        "prompt": "Hello, world!",
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    response = client.post("/generate_text", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "text" in data
    assert "prompt" in data
    assert data["prompt"] == request_data["prompt"]
    assert "model" in data
    assert "usage" in data


def test_generate_text_with_parameters(client):
    """Test text generation with various parameters."""
    request_data = {
        "prompt": "Explain AI in simple terms:",
        "max_tokens": 100,
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 50,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }
    
    response = client.post("/generate_text", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["text"] is not None
    assert data["usage"]["prompt_tokens"] > 0
    assert data["usage"]["completion_tokens"] > 0


def test_generate_text_streaming_not_implemented(client):
    """Test that streaming returns appropriate error."""
    request_data = {
        "prompt": "Test prompt",
        "stream": True
    }
    
    response = client.post("/generate_text", json=request_data)
    assert response.status_code == 400
    assert "Streaming is not yet implemented" in response.json()["detail"]


def test_generate_text_empty_prompt(client):
    """Test that empty prompt is rejected."""
    request_data = {
        "prompt": "",
        "max_tokens": 50
    }
    
    response = client.post("/generate_text", json=request_data)
    assert response.status_code == 422  # Validation error


def test_generate_text_invalid_temperature(client):
    """Test that invalid temperature is rejected."""
    request_data = {
        "prompt": "Test prompt",
        "temperature": 3.0  # Out of range
    }
    
    response = client.post("/generate_text", json=request_data)
    assert response.status_code == 422  # Validation error


def test_generate_text_invalid_max_tokens(client):
    """Test that invalid max_tokens is rejected."""
    request_data = {
        "prompt": "Test prompt",
        "max_tokens": -10  # Negative value
    }
    
    response = client.post("/generate_text", json=request_data)
    assert response.status_code == 422  # Validation error
