# RavensRotoWire Backend

Backend service for RavensRotoWire - An AI-powered text-to-SQL and report generation system using AWS SageMaker LLM endpoints.

## Architecture

This backend service is designed to run on AWS ECS/Fargate and provides:

- **Text-to-SQL Generation**: Convert natural language questions to SQL queries
- **Semantic Retrieval**: RAG-based document retrieval using pgvector
- **Report Generation**: Generate natural language reports from query results
- **LLM Integration**: AWS SageMaker endpoint integration (vLLM/Ollama support)

## Tech Stack

- **Framework**: FastAPI (Python 3.11)
- **LLM Service**: AWS SageMaker Endpoints
- **Database**: Aurora PostgreSQL with pgvector
- **Storage**: Amazon S3
- **Monitoring**: CloudWatch
- **Container**: Docker / ECS Fargate

## Project Structure

```
backend/
├── app/
│   ├── api/                 # API routes
│   │   └── llm_routes.py   # LLM endpoints
│   ├── core/               # Core configuration
│   │   └── config.py       # Settings and environment variables
│   ├── models/             # Pydantic models
│   │   └── schemas.py      # Request/response schemas
│   ├── services/           # Business logic
│   │   └── sagemaker_client.py  # SageMaker LLM client
│   └── main.py             # FastAPI application
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Local development setup
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- AWS Account with SageMaker endpoint deployed
- AWS credentials configured

### Local Development

1. **Clone the repository**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials and SageMaker endpoint details
   ```

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Docker Development

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the services**:
   - Backend API: http://localhost:8000
   - PostgreSQL: localhost:5432

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with service info
- `GET /health` - Health check for load balancer
- `GET /ready` - Readiness check

### LLM Endpoints (`/api/v1/`)

- `POST /generate` - General text generation
- `POST /text2sql` - Convert natural language to SQL
- `POST /retrieve` - Semantic search and retrieval
- `POST /generate-report` - Generate reports from data

## SageMaker Endpoint Configuration

The backend supports multiple LLM deployment formats:

### vLLM Format (Recommended)
```json
{
  "prompt": "Your question here",
  "max_tokens": 2048,
  "temperature": 0.1,
  "top_p": 0.95
}
```

### Ollama Format
```json
{
  "prompt": "Your question here",
  "options": {
    "num_predict": 2048,
    "temperature": 0.1
  }
}
```

## Environment Variables

Key configuration variables:

```bash
# AWS Configuration
AWS_REGION=us-east-1
SAGEMAKER_ENDPOINT_NAME=your-endpoint-name

# LLM Settings
LLM_MODEL_TYPE=vllm  # or ollama
LLM_MAX_TOKENS=2048
LLM_TEMPERATURE=0.1

# Database
DATABASE_HOST=your-aurora-endpoint
DATABASE_NAME=ravens_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# S3 Storage
S3_BUCKET_NAME=your-bucket-name
```

## AWS Deployment

### ECS/Fargate Deployment

1. **Build and push Docker image**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   docker build -t ravens-backend .
   docker tag ravens-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ravens-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ravens-backend:latest
   ```

2. **Create ECS Task Definition**:
   - Configure container with environment variables
   - Set IAM role with SageMaker and S3 permissions
   - Configure CloudWatch logging

3. **Create ECS Service**:
   - Deploy in private subnet
   - Connect to Application Load Balancer
   - Enable auto-scaling

### IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": "arn:aws:sagemaker:*:*:endpoint/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_sagemaker_client.py
```

## Monitoring

The backend integrates with AWS CloudWatch for:
- Application logs
- Error tracking
- Performance metrics
- Health monitoring

## Security Best Practices

1. **Never commit `.env` files** - Use AWS Secrets Manager or Parameter Store
2. **Use IAM roles** for AWS credentials in production
3. **Enable SSL/TLS** for database connections
4. **Configure VPC Security Groups** properly
5. **Use non-root user** in Docker container
6. **Keep dependencies updated** regularly

## Troubleshooting

### SageMaker Connection Issues
- Verify endpoint is in same region
- Check IAM permissions
- Validate endpoint is in service
- Review CloudWatch logs

### Database Connection Issues
- Verify security group rules
- Check VPC configuration
- Validate database credentials
- Test with psql client

## Contributing

1. Create feature branch
2. Make changes
3. Run tests
4. Submit pull request

## License

[Add your license here]

## Support

For issues and questions, please open a GitHub issue.
