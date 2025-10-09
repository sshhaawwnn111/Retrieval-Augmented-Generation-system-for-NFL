#!/bin/bash

# Deploy script for RavensRotoWire Backend to AWS ECS
# Usage: ./deploy.sh [environment] [region]

set -e

ENVIRONMENT=${1:-production}
AWS_REGION=${2:-us-east-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ravens-backend"
IMAGE_TAG=${3:-latest}

echo "🚀 Deploying RavensRotoWire Backend"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${AWS_REGION}"
echo "Account ID: ${ACCOUNT_ID}"
echo "Image: ${ECR_REPO}:${IMAGE_TAG}"

# Login to ECR
echo "📦 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO}

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t ravens-backend:${IMAGE_TAG} .

# Tag image
echo "🏷️  Tagging image..."
docker tag ravens-backend:${IMAGE_TAG} ${ECR_REPO}:${IMAGE_TAG}

# Push to ECR
echo "⬆️  Pushing image to ECR..."
docker push ${ECR_REPO}:${IMAGE_TAG}

# Update ECS service
echo "🔄 Updating ECS service..."
aws ecs update-service \
  --cluster ravens-rotowire-cluster \
  --service ravens-backend-service \
  --force-new-deployment \
  --region ${AWS_REGION}

echo "✅ Deployment initiated successfully!"
echo "Monitor deployment status in AWS Console or run:"
echo "aws ecs describe-services --cluster ravens-rotowire-cluster --services ravens-backend-service --region ${AWS_REGION}"
