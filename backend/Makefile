.PHONY: help install run test docker-build docker-up docker-down clean lint format deploy

help:
	@echo "RavensRotoWire Backend - Available Commands"
	@echo "==========================================="
	@echo "install       - Install Python dependencies"
	@echo "run           - Run the FastAPI application"
	@echo "test          - Run tests with pytest"
	@echo "docker-build  - Build Docker image"
	@echo "docker-up     - Start services with docker-compose"
	@echo "docker-down   - Stop docker-compose services"
	@echo "clean         - Clean up cache and build files"
	@echo "lint          - Run linting with flake8"
	@echo "format        - Format code with black"
	@echo "deploy        - Deploy to AWS ECS"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html

docker-build:
	docker build -t ravens-backend:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

lint:
	flake8 app/ --max-line-length=100 --exclude=__pycache__

format:
	black app/ tests/ --line-length=100

deploy:
	./deploy.sh production us-east-1

dev-setup: install
	cp .env.example .env
	@echo "✅ Development environment set up!"
	@echo "⚠️  Please edit .env with your AWS credentials"
