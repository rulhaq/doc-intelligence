# Deployment Guide

## Prerequisites

### Development
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Production
- Kubernetes cluster (1.25+)
- Helm 3.x
- kubectl configured
- Container registry (Azure ACR, Docker Hub, etc.)
- Domain name and SSL certificates

## Development Deployment

### 1. Setup Environment

```bash
# Clone repository
git clone <repository>
cd customerllm

# Copy environment file
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python scripts/create_admin.py \
  --email admin@example.com \
  --password changeme
```

### 4. Initialize Ollama

```bash
# Pull Jais model (or substitute)
bash scripts/init-ollama.sh
```

### 5. Access Application

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard
- Grafana: http://localhost:3001 (admin/admin)

## Production Deployment (Kubernetes)

### 1. Prepare Images

```bash
# Set registry URL
export REGISTRY="your-registry.azurecr.io"

# Build images
docker build -t $REGISTRY/customerllm-backend:latest ./backend
docker build -t $REGISTRY/customerllm-frontend:latest ./frontend
docker build -t $REGISTRY/customerllm-ocr-worker:latest ./ocr-worker

# Push to registry
docker push $REGISTRY/customerllm-backend:latest
docker push $REGISTRY/customerllm-frontend:latest
docker push $REGISTRY/customerllm-ocr-worker:latest
```

### 2. Create Namespace

```bash
kubectl apply -f infrastructure/kubernetes/namespace.yaml
```

### 3. Create Secrets

```bash
# Create secrets (do NOT use example values in production!)
kubectl create secret generic customerllm-secrets \
  --from-literal=postgres-db=customerllm \
  --from-literal=postgres-user=customerllm \
  --from-literal=postgres-password=<SECURE_PASSWORD> \
  --from-literal=database-url=postgresql://customerllm:<PASSWORD>@postgres:5432/customerllm \
  --from-literal=redis-url=redis://redis:6379/0 \
  --from-literal=secret-key=<GENERATE_SECURE_32_CHAR_KEY> \
  --from-literal=s3-access-key=<ACCESS_KEY> \
  --from-literal=s3-secret-key=<SECRET_KEY> \
  -n customerllm
```

### 4. Deploy Services

```bash
# Deploy database
kubectl apply -f infrastructure/kubernetes/postgres.yaml

# Deploy Qdrant
kubectl apply -f infrastructure/kubernetes/qdrant.yaml

# Deploy Redis
kubectl apply -f infrastructure/kubernetes/redis.yaml

# Deploy backend
kubectl apply -f infrastructure/kubernetes/backend.yaml

# Deploy frontend
kubectl apply -f infrastructure/kubernetes/frontend.yaml

# Deploy ingress
kubectl apply -f infrastructure/kubernetes/ingress.yaml
```

### 5. Wait for Deployment

```bash
# Check deployment status
kubectl get pods -n customerllm

# Wait for ready
kubectl wait --for=condition=available --timeout=300s \
  deployment/backend -n customerllm

kubectl wait --for=condition=available --timeout=300s \
  deployment/frontend -n customerllm
```

### 6. Run Migrations

```bash
# Run database migrations
kubectl exec -it deployment/backend -n customerllm -- alembic upgrade head

# Create admin user
kubectl exec -it deployment/backend -n customerllm -- \
  python scripts/create_admin.py \
  --email admin@example.com \
  --password <SECURE_PASSWORD>
```

### 7. Configure DNS

Point your domain to the ingress load balancer IP:

```bash
# Get ingress IP
kubectl get ingress -n customerllm
```

Add DNS A record: `customerllm.example.com` → `<INGRESS_IP>`

### 8. Verify Deployment

```bash
# Check all resources
kubectl get all -n customerllm

# Check logs
kubectl logs -f deployment/backend -n customerllm

# Test health
curl https://customerllm.example.com/api/v1/health
```

## Scaling

### Backend Scaling

```bash
# Manual scaling
kubectl scale deployment backend --replicas=5 -n customerllm

# Auto-scaling is configured via HPA (see backend.yaml)
kubectl get hpa -n customerllm
```

### Database Scaling

For production, consider managed PostgreSQL:
- AWS RDS
- Azure Database for PostgreSQL
- Google Cloud SQL

Update `DATABASE_URL` secret accordingly.

### Qdrant Scaling

For large deployments:
1. Use Qdrant Cloud (managed)
2. Or deploy Qdrant cluster with replication

## Monitoring

### Prometheus

```bash
# Access Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n customerllm
```

Visit: http://localhost:9090

### Grafana

```bash
# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n customerllm
```

Visit: http://localhost:3000 (admin/admin)

## Backup & Restore

### Database Backup

```bash
# Backup
kubectl exec -it deployment/postgres -n customerllm -- \
  pg_dump -U customerllm customerllm > backup.sql

# Restore
kubectl exec -i deployment/postgres -n customerllm -- \
  psql -U customerllm customerllm < backup.sql
```

### Qdrant Backup

```bash
# Create snapshot
curl -X POST http://qdrant:6333/collections/documents/snapshots

# Download snapshot
curl http://qdrant:6333/collections/documents/snapshots/<snapshot_name> \
  -o qdrant-snapshot.tar

# Restore snapshot
curl -X PUT http://qdrant:6333/collections/documents/snapshots/upload \
  -H "Content-Type: multipart/form-data" \
  -F "snapshot=@qdrant-snapshot.tar"
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
kubectl logs deployment/backend -n customerllm

# Check database connection
kubectl exec -it deployment/backend -n customerllm -- \
  python -c "from app.core.database import engine; print(engine.connect())"
```

### Qdrant connection issues

```bash
# Check Qdrant health
kubectl exec -it deployment/qdrant -n customerllm -- \
  curl http://localhost:6333/health

# Check collections
kubectl exec -it deployment/qdrant -n customerllm -- \
  curl http://localhost:6333/collections
```

### OCR processing fails

```bash
# Check OCR worker logs
kubectl logs deployment/ocr-worker -n customerllm

# Test OCR worker
kubectl exec -it deployment/ocr-worker -n customerllm -- \
  curl http://localhost:8001/health
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Generate secure SECRET_KEY (32+ characters)
- [ ] Enable TLS/HTTPS (Let's Encrypt or commercial cert)
- [ ] Configure network policies
- [ ] Enable audit logging
- [ ] Set up RBAC properly
- [ ] Use secrets manager (Azure Key Vault, AWS Secrets Manager)
- [ ] Enable pod security policies
- [ ] Configure resource limits
- [ ] Set up monitoring and alerting
- [ ] Configure backup schedule
- [ ] Test disaster recovery

