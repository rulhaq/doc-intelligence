# CustomerLLM - OpenShift AI / vLLM RAG Assistant

CustomerLLM is a prosecutor-facing RAG chatbot that runs on OpenShift and uses vLLM OpenAI-compatible endpoints for both chat and embeddings. All configuration is environment-driven and compatible with `envFrom: secretRef`.

## Architecture

```
User -> Frontend (React) -> Backend (FastAPI) -> Qdrant
                                   |
                                   +-> vLLM (OpenAI-compatible /v1)
                                   +-> Postgres, Redis, Object Storage
                                   +-> OCR Worker
```

## Requirements
- OpenShift or Kubernetes (OpenShift recommended)
- vLLM deployed as OpenAI-compatible endpoints
- Podman on jump server for image builds
- `oc` CLI configured to target cluster namespace

## Environment Variables (Required)

These must be supplied via `envFrom: secretRef` (no `.env` at runtime):

```
APP_ENV
DEBUG
BACKEND_HOST
BACKEND_PORT
BACKEND_URL
FRONTEND_URL
CORS_ORIGINS

VLLM_BASE_URL
VLLM_MODEL
VLLM_EMBEDDING_BASE_URL
VLLM_EMBEDDING_MODEL
VLLM_API_TOKEN
VLLM_TIMEOUT
EMBEDDINGS_PROVIDER
TEI_BASE_URL
TEI_API_TOKEN
TEI_TIMEOUT

DATABASE_URL
REDIS_URL
QDRANT_URL
QDRANT_COLLECTION_NAME
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
STORAGE_MODE
FILE_STORAGE_PATH

OCR_WORKER_URL
OCR_WORKER_PORT
SECRET_KEY
```

See `env.example` for a full template.

## Deploy on OpenShift (Jump Server)

1) Clone repo

```
git clone <repo>
cd <repo>
```

2) Create `.env.openshift`

```
cp env.example .env.openshift
```

3) Create secret

```
oc create secret generic customerllm-env --from-env-file=.env.openshift
```

4) Apply manifests

```
oc apply -f k8s/
```

5) Verify pods and PVC

```
oc get pods
oc get pvc
```

6) Test vLLM connectivity from backend pod

```
oc rsh deploy/customerllm-backend
curl -H "Authorization: Bearer $VLLM_API_TOKEN" $VLLM_BASE_URL/v1/models
```

Optional image builds from jump server:

```
podman build -t customerllm-backend ./backend
podman build -t customerllm-frontend ./frontend
podman build -t customerllm-ocr-worker ./ocr-worker
```

## Health Endpoints
- Backend: `/health`, `/ready`
- OCR Worker: `/health`, `/ready`

## vLLM OpenAI Compatibility
The backend and OCR worker only call:
- `POST /v1/chat/completions`
- `POST /v1/embeddings`

The vLLM base URLs are normalized internally and `/v1` is appended by the client.

## License
Proprietary - All Rights Reserved
