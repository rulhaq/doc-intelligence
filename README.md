# CustomerLLM - Enterprise AI Chat & Document Intelligence Platform

A production-ready, private-AI enterprise application featuring:
- **Bespoke Chat UI** with contextual cards and preview pane
- **Admin OCR Portal** for PDF upload, preview, and manual corrections
- **Vector Search** powered by Qdrant
- **On-Premise AI** using Ollama (Jais) for MVP, RHELAI + vLLM for production
- **Agent Manager** with MCP plugin architecture
- **Enterprise Auth** (OAuth2, SAML, Local JWT)
- **DMZ-Capable Architecture** for secure on-premise deployment

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  React Frontend │────▶│  FastAPI Backend│────▶│  Qdrant Vector  │
│  Chat + Admin   │     │  + Agent Manager│     │      DB         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ├────▶ Ollama (Jais) / RHELAI+vLLM
                              ├────▶ PaddleOCR Worker
                              ├────▶ MinIO / Object Storage
                              └────▶ Redis (Task Queue)
```

## Quick Start (MVP - Docker Compose)

### Prerequisites
- Docker & Docker Compose
- 16GB+ RAM
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Clone and Setup

```bash
git clone <repository>
cd <repository>

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Qdrant Dashboard: http://localhost:6333/dashboard
# - Grafana: http://localhost:3001
```

### 3. Initialize System

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python scripts/create_admin.py --email admin@example.com --password changeme

# Test the system
curl http://localhost:8000/health
```

## Project Structure

```
.
├── frontend/               # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Chat & Admin pages
│   │   ├── services/      # API clients
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript definitions
│   └── package.json
│
├── backend/               # FastAPI + Python
│   ├── app/
│   │   ├── api/          # REST & WebSocket endpoints
│   │   ├── core/         # Config, security, dependencies
│   │   ├── services/     # Business logic
│   │   │   ├── ocr/      # PaddleOCR pipeline
│   │   │   ├── vector/   # Qdrant integration
│   │   │   ├── agents/   # Agent manager
│   │   │   └── inference/ # LLM connectors
│   │   ├── models/       # SQLAlchemy models
│   │   └── workers/      # Celery tasks
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── infrastructure/        # Deployment configs
│   ├── docker/           # Docker configs
│   ├── kubernetes/       # K8s manifests
│   ├── helm/             # Helm charts
│   └── monitoring/       # Prometheus, Grafana
│
├── ocr-worker/           # Dedicated OCR service
│   ├── app/
│   │   ├── ocr_engine.py # PaddleOCR + layoutparser
│   │   └── llm_corrector.py # OCR correction with LLM
│   └── Dockerfile
│
├── docs/                 # Documentation
│   ├── API.md           # API documentation
│   ├── DEPLOYMENT.md    # Deployment guide
│   ├── SECURITY.md      # Security guidelines
│   └── RUNBOOK.md       # Operations runbook
│
├── scripts/             # Utility scripts
├── tests/               # Integration tests
├── docker-compose.yml   # MVP deployment
└── README.md
```

## Key Features

### 🔐 Enterprise Authentication
- OAuth2 (Azure AD, Google, GitHub)
- SAML 2.0 SSO
- Local JWT with refresh tokens
- Role-Based Access Control (Admin, Editor, Viewer)

### 📄 Intelligent Document Processing
- PaddleOCR with layout detection
- LLM-powered OCR correction (Jais)
- Side-by-side preview with editable text
- Confidence scoring and audit trail

### 💬 Bespoke Chat Interface
- Real-time streaming responses (WebSocket)
- Contextual cards with source provenance
- Preview pane with highlighted snippets
- Semantic search with filters

### 🤖 Agent Manager & MCP
- Plugin architecture for custom agents
- Web scraping, connector agents
- Isolated execution environment
- Authenticated internal API

### 🔍 Vector Search (Qdrant)
- Semantic chunking (500 tokens, 50% overlap)
- Metadata filtering (source, date, confidence)
- Hybrid search (dense + sparse)
- Horizontal scaling support

### 📊 Observability
- Prometheus metrics
- Grafana dashboards
- OpenSearch/ELK logging
- Request tracing
- Audit logs

## API Documentation

### Authentication

```bash
# Local login
curl -X POST http://localhost:8000/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@example.com", "password": "changeme"}'

# OAuth start (redirect)
curl http://localhost:8000/auth/oauth/start?provider=azure
```

### Chat API

```bash
# Create conversation
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Contract Analysis"}'

# Send message (streaming)
curl -X POST http://localhost:8000/api/v1/conversations/{id}/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "text": "Find termination clauses",
    "contextFilters": {"source": ["contracts"]}
  }'
```

### Admin API

```bash
# Upload PDF
curl -X POST http://localhost:8000/api/v1/admin/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@contract.pdf"

# Process OCR
curl -X POST http://localhost:8000/api/v1/admin/documents/{id}/process-ocr \
  -H "Authorization: Bearer $TOKEN"

# Get preview
curl http://localhost:8000/api/v1/admin/documents/{id}/preview \
  -H "Authorization: Bearer $TOKEN"

# Commit to vector DB
curl -X POST http://localhost:8000/api/v1/admin/documents/{id}/commit \
  -H "Authorization: Bearer $TOKEN"
```

See [docs/API.md](docs/API.md) for complete API reference.

## Production Deployment (Kubernetes)

### Prerequisites
- Kubernetes cluster (1.25+)
- Helm 3.x
- kubectl configured
- Container registry access

### Deploy with Helm

```bash
# Add custom registry (if needed)
helm repo add customer-llm https://registry.example.com/charts

# Install with custom values
helm install customer-llm ./infrastructure/helm/customer-llm \
  --namespace customer-llm \
  --create-namespace \
  --values production-values.yaml

# Verify deployment
kubectl get pods -n customer-llm
kubectl get ingress -n customer-llm
```

### Production Considerations

1. **Inference**: Replace Ollama with RHELAI + vLLM endpoints
2. **Scaling**: Configure HorizontalPodAutoscaler
3. **Storage**: Use persistent volumes for Qdrant
4. **Secrets**: Use external secrets operator
5. **Network**: DMZ configuration for agent internet access
6. **Monitoring**: Connect to enterprise Prometheus/Grafana
7. **Backup**: Regular Qdrant snapshots

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed guide.

## Security

### Key Security Features
- TLS 1.3 everywhere
- Encryption at rest (disk + object storage)
- KMS for secrets management
- Network segmentation (DMZ)
- RBAC with least privilege
- Audit logging for compliance
- Rate limiting and DDoS protection
- PII detection and redaction (optional)

See [docs/SECURITY.md](docs/SECURITY.md) for security guidelines.

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run migrations
alembic upgrade head

# Start dev server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v --cov=app
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Type check
npm run type-check
```

### OCR Worker Development

```bash
cd ocr-worker

# Install dependencies
pip install -r requirements.txt

# Start worker
python app/worker.py
```

## Testing

```bash
# Backend unit tests
cd backend && pytest

# Frontend unit tests
cd frontend && npm test

# Integration tests
python tests/integration/test_end_to_end.py

# Load tests
locust -f tests/load/locustfile.py
```

## Monitoring & Observability

### Metrics (Prometheus)
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `ocr_processing_duration_seconds` - OCR pipeline duration
- `qdrant_vector_count` - Number of vectors in DB
- `llm_inference_duration_seconds` - LLM inference time
- `agent_task_status` - Agent task status

### Dashboards (Grafana)
- System Overview
- API Performance
- OCR Pipeline Metrics
- Vector DB Health
- Agent Activity

Access Grafana at http://localhost:3001 (admin/admin)

## Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine.connect())"
```

**OCR processing fails**
```bash
# Check OCR worker
docker-compose logs ocr-worker

# Verify PaddleOCR installation
docker-compose exec ocr-worker python -c "from paddleocr import PaddleOCR; print('OK')"
```

**Qdrant connection issues**
```bash
# Check Qdrant health
curl http://localhost:6333/health

# Verify collection exists
curl http://localhost:6333/collections
```

See [docs/RUNBOOK.md](docs/RUNBOOK.md) for operational procedures.

## License

Proprietary - All Rights Reserved

## Support

For issues and questions:
- Internal Wiki: [link]
- Email: support@example.com
- Slack: #customer-llm-support

