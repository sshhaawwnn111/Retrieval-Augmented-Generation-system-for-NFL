# Quick Start Guide - RavensRotoWire Backend

## 🚀 Getting Started in 5 Minutes

### 1. Set Up Environment

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials
```

### 2. Configure AWS SageMaker Endpoint

In your `.env` file, set:

```bash
SAGEMAKER_ENDPOINT_NAME=your-endpoint-name
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### 3. Run Locally

```bash
# Option 1: Direct Python
uvicorn app.main:app --reload

# Option 2: Using Make
make run

# Option 3: Using Docker
docker-compose up
```

### 4. Test the API

Visit http://localhost:8000/docs for interactive API documentation.

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Generate Text:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain what a touchdown is",
    "max_tokens": 100
  }'
```

**Text-to-SQL:**
```bash
curl -X POST "http://localhost:8000/api/v1/text2sql" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me all players on the Ravens team",
    "schema_context": "Table: players (id, name, team, position)"
  }'
```

## 🔧 Development Commands

```bash
# Run tests
make test

# Format code
make format

# Run linter
make lint

# Clean cache files
make clean
```

## 🐳 Docker Development

```bash
# Start all services (backend + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## ☁️ AWS Deployment

### Prerequisites
1. Create SageMaker endpoint with vLLM/Ollama
2. Set up Aurora PostgreSQL with pgvector
3. Create S3 bucket for data storage
4. Create ECR repository
5. Create ECS cluster and service

### Deploy

```bash
# Build and push to ECR
make deploy

# Or manually
./deploy.sh production us-east-1
```

## 📊 Monitoring

- **Logs**: CloudWatch Logs `/aws/ecs/ravens-rotowire`
- **Metrics**: CloudWatch Metrics for ECS service
- **Health**: ALB health checks on `/health` endpoint

## 🔐 Security Checklist

- [ ] Never commit `.env` file
- [ ] Use IAM roles in production (not access keys)
- [ ] Enable SSL for database connections
- [ ] Configure Security Groups properly
- [ ] Use Secrets Manager for sensitive data
- [ ] Enable CloudTrail logging
- [ ] Set up VPC with private subnets

## 🐛 Troubleshooting

### SageMaker Connection Failed
```bash
# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name your-endpoint-name

# Test IAM permissions
aws sagemaker-runtime invoke-endpoint --endpoint-name your-endpoint-name \
  --body '{"prompt":"test"}' --content-type application/json output.json
```

### Database Connection Failed
```bash
# Test connection
psql -h your-db-endpoint -U postgres -d ravens_db

# Check security group
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### Docker Build Failed
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

## 📚 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/docs` | API documentation |
| POST | `/api/v1/generate` | Text generation |
| POST | `/api/v1/text2sql` | Natural language to SQL |
| POST | `/api/v1/retrieve` | Semantic search |
| POST | `/api/v1/generate-report` | Report generation |

## 🔄 Next Steps

1. **Implement Database Layer**: Add SQLAlchemy models and database connection
2. **Add Authentication**: Implement JWT or API key authentication
3. **Implement RAG**: Add vector search with pgvector
4. **Add Caching**: Implement Redis for response caching
5. **Set Up CI/CD**: GitHub Actions for automated deployments
6. **Add Rate Limiting**: Protect endpoints from abuse
7. **Implement Monitoring**: Add custom CloudWatch metrics

## 📞 Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [API documentation](http://localhost:8000/docs)
- Open a GitHub issue
