#!/bin/bash
set -e

echo "CustomerLLM Deployment Script"
echo "=============================="

# Load environment
ENV=${1:-development}
echo "Environment: $ENV"

if [ "$ENV" = "production" ]; then
    echo "Deploying to production..."
    
    # Build and push Docker images
    echo "Building Docker images..."
    docker build -t customerllm-backend:latest ./backend
    docker build -t customerllm-frontend:latest ./frontend
    docker build -t customerllm-ocr-worker:latest ./ocr-worker
    
    # Tag and push (replace with your registry)
    REGISTRY="your-registry.azurecr.io"
    docker tag customerllm-backend:latest $REGISTRY/customerllm-backend:latest
    docker tag customerllm-frontend:latest $REGISTRY/customerllm-frontend:latest
    docker tag customerllm-ocr-worker:latest $REGISTRY/customerllm-ocr-worker:latest
    
    docker push $REGISTRY/customerllm-backend:latest
    docker push $REGISTRY/customerllm-frontend:latest
    docker push $REGISTRY/customerllm-ocr-worker:latest
    
    # Apply Kubernetes manifests
    echo "Applying Kubernetes manifests..."
    kubectl apply -f infrastructure/kubernetes/namespace.yaml
    kubectl apply -f infrastructure/kubernetes/secrets.yaml
    kubectl apply -f infrastructure/kubernetes/postgres.yaml
    kubectl apply -f infrastructure/kubernetes/qdrant.yaml
    kubectl apply -f infrastructure/kubernetes/backend.yaml
    kubectl apply -f infrastructure/kubernetes/frontend.yaml
    kubectl apply -f infrastructure/kubernetes/ingress.yaml
    
    echo "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/backend -n customerllm
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n customerllm
    
    echo "Production deployment complete!"
    
else
    echo "Starting development environment..."
    docker-compose up -d
    
    echo "Waiting for services to be healthy..."
    sleep 10
    
    echo "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head
    
    echo "Development environment started!"
    echo "Access the application at: http://localhost:3000"
    echo "API docs at: http://localhost:8000/docs"
fi

