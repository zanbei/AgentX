#!/bin/bash

# Exit on error
set -e

# Check if AWS region is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <aws-region> [aws-account-id]"
  echo "Example: $0 us-east-1 123456789012"
  exit 1
fi

AWS_REGION=$1

# Get AWS account ID if not provided
if [ -z "$2" ]; then
  AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
  if [ $? -ne 0 ]; then
    echo "Error: Failed to get AWS account ID. Please provide it as the second argument."
    exit 1
  fi
else
  AWS_ACCOUNT_ID=$2
fi

# ECR registry URL
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Function to create ECR repository if it doesn't exist
create_repository() {
  local repo_name=$1
  aws ecr describe-repositories --repository-names ${repo_name} --region ${AWS_REGION} > /dev/null 2>&1 || \
  aws ecr create-repository --repository-name ${repo_name} --region ${AWS_REGION}
}

# Login to ECR
echo "Logging in to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Build and push backend image
echo "Building and pushing backend image..."
create_repository "agentx-be"
cd be
docker build -t agentx-be .
docker tag agentx-be:latest ${ECR_REGISTRY}/agentx-be:latest
docker push ${ECR_REGISTRY}/agentx-be:latest
cd ..

# Build and push frontend image
echo "Building and pushing frontend image..."
create_repository "agentx-fe"
cd fe
docker build -t agentx-fe .
docker tag agentx-fe:latest ${ECR_REGISTRY}/agentx-fe:latest
docker push ${ECR_REGISTRY}/agentx-fe:latest
cd ..

# Build and push MCP MySQL image
echo "Building and pushing MCP MySQL image..."
create_repository "agentx-mcp-mysql"
cd mcp/mysql
docker build -t agentx-mcp-mysql .
docker tag agentx-mcp-mysql:latest ${ECR_REGISTRY}/agentx-mcp-mysql:latest
docker push ${ECR_REGISTRY}/agentx-mcp-mysql:latest
cd ../..

# Build and push MCP Redshift image
echo "Building and pushing MCP Redshift image..."
create_repository "agentx-mcp-redshift"
cd mcp/redshift
docker build -t agentx-mcp-redshift .
docker tag agentx-mcp-redshift:latest ${ECR_REGISTRY}/agentx-mcp-redshift:latest
docker push ${ECR_REGISTRY}/agentx-mcp-redshift:latest
cd ../..

echo "All images have been built and pushed to ECR."
echo "Next steps:"
echo "1. cd cdk"
echo "2. npm install"
echo "3. cdk bootstrap (if not already done)"
echo "4. cdk deploy"
