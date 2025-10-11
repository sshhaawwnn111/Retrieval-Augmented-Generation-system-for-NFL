# vLLM Text Generation Service

A production-ready, high-throughput LLM inference service built with FastAPI and vLLM. This service provides a simple REST API for text generation with support for various LLM models.

## Features

- 🚀 **High-throughput inference** using vLLM
- 🔌 **Simple REST API** with FastAPI
- 🎛️ **Flexible generation parameters** (temperature, top_p, top_k, etc.)
- 🐳 **Docker support** with GPU acceleration
- 📊 **Token usage tracking** for each request
- 🏥 **Health check endpoint** for monitoring
- 📝 **Comprehensive API documentation** (Swagger/OpenAPI)

## Architecture

```
llm/
├── main.py                 # FastAPI application with vLLM integration
├── config.py              # Configuration management
├── schemas.py             # Pydantic request/response models
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── Makefile              # Build and run commands
└── README.md             # This file
```

## Requirements

### Hardware
- NVIDIA GPU with CUDA support (recommended for production)
- At least 16GB GPU memory for 7B models
- 32GB+ GPU memory for larger models

### Software
- Python 3.10+
- CUDA 12.1+ (for GPU acceleration)
- Docker with nvidia-docker (for containerized deployment)

## Quick Start

### Option 1: Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your model configuration
```

3. **Run the service**:
```bash
python main.py
```

Or use the Makefile:
```bash
make install
make run
```

The service will start on `http://localhost:8001`

### Option 2: Docker (Recommended)

1. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

Or use the Makefile:
```bash
make docker-build
make docker-run
```

2. **Check logs**:
```bash
docker-compose logs -f
```

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

### Service Configuration
- `SERVICE_HOST`: Host to bind (default: `0.0.0.0`)
- `SERVICE_PORT`: Port to listen on (default: `8001`)

### Model Configuration
- `MODEL_NAME`: HuggingFace model ID (default: `meta-llama/Llama-2-7b-chat-hf`)
- `MODEL_REVISION`: Model revision/branch (default: `main`)
- `TENSOR_PARALLEL_SIZE`: Number of GPUs for tensor parallelism (default: `1`)
- `GPU_MEMORY_UTILIZATION`: GPU memory utilization ratio (default: `0.9`)
- `MAX_MODEL_LEN`: Maximum sequence length (default: `4096`)

### Generation Defaults
- `DEFAULT_MAX_TOKENS`: Default max tokens to generate (default: `512`)
- `DEFAULT_TEMPERATURE`: Default sampling temperature (default: `0.7`)
- `DEFAULT_TOP_P`: Default nucleus sampling parameter (default: `0.95`)

### Example Models

You can use any compatible HuggingFace model:
- `meta-llama/Llama-2-7b-chat-hf` (requires HF access)
- `meta-llama/Llama-2-13b-chat-hf` (requires more GPU memory)
- `mistralai/Mistral-7B-Instruct-v0.2`
- `tiiuae/falcon-7b-instruct`

## API Documentation

Once the service is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Endpoints

#### `POST /generate_text`

Generate text from a prompt.

**Request Body**:
```json
{
  "prompt": "Write a short story about a robot learning to paint:",
  "max_tokens": 256,
  "temperature": 0.8,
  "top_p": 0.95,
  "top_k": 50,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "stop": ["\\n\\n"],
  "stream": false
}
```

**Response**:
```json
{
  "text": "In a small workshop, a robot named Artie discovered...",
  "prompt": "Write a short story about a robot learning to paint:",
  "model": "meta-llama/Llama-2-7b-chat-hf",
  "finish_reason": "stop",
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 156,
    "total_tokens": 168
  }
}
```

**Parameters**:
- `prompt` (required): Input text prompt
- `max_tokens` (optional): Maximum tokens to generate (1-4096)
- `temperature` (optional): Sampling temperature (0.0-2.0)
- `top_p` (optional): Nucleus sampling parameter (0.0-1.0)
- `top_k` (optional): Top-k sampling parameter
- `frequency_penalty` (optional): Frequency penalty (0.0-2.0)
- `presence_penalty` (optional): Presence penalty (0.0-2.0)
- `stop` (optional): List of stop sequences
- `stream` (optional): Enable streaming (not yet implemented)

#### `GET /health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "model": "meta-llama/Llama-2-7b-chat-hf",
  "vllm_version": "0.3.0"
}
```

#### `GET /model_info`

Get information about the loaded model.

**Response**:
```json
{
  "model_name": "meta-llama/Llama-2-7b-chat-hf",
  "model_revision": "main",
  "tensor_parallel_size": 1,
  "gpu_memory_utilization": 0.9,
  "max_model_len": 4096,
  "default_max_tokens": 512,
  "default_temperature": 0.7,
  "default_top_p": 0.95
}
```

## Usage Examples

### cURL

```bash
curl -X POST "http://localhost:8001/generate_text" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms:",
    "max_tokens": 200,
    "temperature": 0.7
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8001/generate_text",
    json={
        "prompt": "Explain quantum computing in simple terms:",
        "max_tokens": 200,
        "temperature": 0.7
    }
)

result = response.json()
print(result["text"])
```

### JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:8001/generate_text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'Explain quantum computing in simple terms:',
    max_tokens: 200,
    temperature: 0.7
  })
});

const result = await response.json();
console.log(result.text);
```

## Development

### Running in Development Mode

Use the development mode with auto-reload:

```bash
make dev
```

Or manually:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Code Quality

Format code:
```bash
make format
```

Run linter:
```bash
make lint
```

### Testing

Run tests:
```bash
make test
```

## Performance Optimization

### Multi-GPU Setup

For better performance with larger models, use tensor parallelism:

```bash
# In .env
TENSOR_PARALLEL_SIZE=2  # Use 2 GPUs
```

### Memory Optimization

Adjust GPU memory utilization:

```bash
# In .env
GPU_MEMORY_UTILIZATION=0.85  # Use 85% of GPU memory
```

### Batch Processing

vLLM automatically batches requests for optimal throughput. No configuration needed!

## Troubleshooting

### Out of Memory Errors

1. Reduce `MAX_MODEL_LEN` in configuration
2. Decrease `GPU_MEMORY_UTILIZATION`
3. Use a smaller model
4. Enable tensor parallelism with multiple GPUs

### Slow Startup

Model loading can take 1-5 minutes depending on:
- Model size
- Network speed (for downloading)
- GPU performance

The service caches models in `~/.cache/huggingface` to speed up subsequent starts.

### CUDA/GPU Issues

Ensure:
1. NVIDIA drivers are installed
2. CUDA toolkit is compatible
3. nvidia-docker is configured (for Docker deployments)

Check GPU availability:
```bash
nvidia-smi
```

## Integration with Backend

To integrate with the RavensRotoWire backend:

1. Update backend's `.env`:
```bash
LLM_SERVICE_URL=http://llm-service:8001
```

2. Update backend's `docker-compose.yml` to include the LLM service network:
```yaml
networks:
  - ravensrotowire-network
```

3. Call the service from backend:
```python
import httpx

async def generate_text(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://llm-service:8001/generate_text",
            json={"prompt": prompt}
        )
        return response.json()
```

## Production Deployment

### Environment Variables

Set these in production:
- Use environment-specific `.env` files
- Store sensitive values (HF_TOKEN) in secrets manager
- Configure appropriate resource limits

### Monitoring

- Health endpoint: `/health`
- Model info endpoint: `/model_info`
- Consider adding Prometheus metrics

### Scaling

- Deploy multiple replicas behind a load balancer
- Use tensor parallelism for single large models
- Use pipeline parallelism for very large models

## License

This service is part of the RavensRotoWire project.

## Support

For issues and questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review vLLM documentation: https://docs.vllm.ai/
3. Open an issue in the repository
