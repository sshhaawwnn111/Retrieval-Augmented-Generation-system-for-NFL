# Makefile for LLM Service

.PHONY: help install dev run docker-build docker-run docker-stop test clean

# Variables
PYTHON := python3
PIP := pip3
SERVICE_NAME := vllm-service
PORT := 8001

help:
	@echo "LLM Service - Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Run in development mode"
	@echo "  make run           - Run the service"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with Docker Compose"
	@echo "  make docker-stop   - Stop Docker containers"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean up cache and temp files"

install:
	$(PIP) install -r requirements.txt

dev:
	$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port $(PORT)

run:
	$(PYTHON) main.py

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	$(PYTHON) -m pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

format:
	black .

lint:
	flake8 .
