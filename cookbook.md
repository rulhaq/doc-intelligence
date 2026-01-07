# Cookbook: End-to-End Deployment on OpenShift AI

**vLLM (OCI/Quay) + PVC Storage + Token-Protected Routes**

This cookbook explains **every step**, from the moment you receive access to a **jump server**, until the application is **fully running and connected** to LLM and embedding models deployed on **Red Hat OpenShift AI (RHOAI)** using **vLLM**.

This is a **POC-ready but enterprise-grade** deployment guide.

---

## Architecture Overview (Read First)

The system consists of **two independent parts**:

1. **Models (Managed by OpenShift AI)**

   - LLM model (vLLM via OCI / Quay)
   - Embedding model (TEI – Text Embeddings Inference)
   - Deployed from **OCI / Quay**
   - Exposed via **token-protected Routes**

2. **Application (This GitHub Repository)**

   - Backend API (RAG, guardrails, orchestration)
   - Frontend UI
   - OCR worker
   - Vector DB (Qdrant)
   - Persistent PDF storage via **PVC**

**Important:**
👉 The application **does NOT host models**.
👉 It connects to: - vLLM for chat (token-protected Route) - TEI for embeddings (internal service)

---

## 1. Prerequisites

### Jump Server Requirements

Ensure the jump server has:

```bash
git --version
oc version
podman --version
```

You must have:

- Network access to the OpenShift cluster
- Permission to create:

  - Secrets
  - PVCs
  - Deployments
  - Services
  - Routes
  - InferenceServices (OpenShift AI)

---

### Information You Must Have Before Starting

- OpenShift API URL
- Login token or kubeconfig
- Target namespace / project
- OCI / Quay model image references
- Bearer token for accessing vLLM Routes
- A RWX-capable StorageClass (for PVC)

---

## 2. Login to OpenShift from the Jump Server

```bash
oc login https://<cluster-api>:6443 --token=<TOKEN>
oc project <namespace>
```

Verify access:

```bash
oc whoami
oc get pods
```

---

## 3. Clone the Source Code (Correct Branch)

Clone the repository and **checkout the vLLM branch**:

```bash
git clone https://github.com/<org>/<repo>.git
cd <repo>
git checkout vllm
```

git clone -b <branch-name> <repository-url>

### Repository Structure (High Level)

```
backend/        # API, RAG logic, vLLM client
frontend/       # Web UI
ocr-worker/     # PDF OCR processing
k8s/            # OpenShift manifests
env.example     # Environment variable template
cookbook.md    # This file
```

---

## 4. Deploy LLM & Embedding Models on OpenShift AI (OCI / Quay)

https://github.com/redhat-ai-services/modelcar-catalog

This section follows the same flow as the RHOAI vLLM OCI deployment pattern.

### 4.1 Create / Select a Data Science Project

In the OpenShift console:

- Navigate to **OpenShift AI**
- Create or select a **Data Science Project**

---

### 4.2 Deploy the LLM Model (vLLM)

1. Go to **Models → Deploy Model**
2. Select:

   - **Serving Runtime:** vLLM
   - **Model Source:** OCI

3. Provide:

   - Quay image reference (LLM)
   - Model name (e.g. `granite-8b-instruct`)

4. Configure:

   - GPU resources
   - Replicas = 1 (POC)

5. Enable **External Route**
6. Apply / Deploy

---

### 4.3 Deploy Embeddings with TEI (NOT OpenShift AI)

**Important:** In this POC, embeddings are **not** served by OpenShift AI / vLLM.  
Instead, embeddings are served by **TEI (Text Embeddings Inference)** using a prebuilt container image.

Why:

- The OpenShift AI ModelCar catalog embedding options are limited (and may be English-only).
- Our knowledge base is Arabic PDFs, so we need a multilingual embedding model.
- TEI lets us run a strong multilingual embedding model without building our own OCI image.

#### 4.3.1 What TEI Is

TEI = **Text Embeddings Inference** (Hugging Face)  
It runs as a normal Kubernetes deployment and provides an HTTP API that returns embeddings vectors.

In our application:

- Backend calls TEI over the internal cluster network:
  - `TEI_BASE_URL=http://tei:8080`
- The backend uses TEI endpoint:
  - `POST /embed`

#### 4.3.2 Deploy TEI into the same namespace as the app

TEI is deployed using the repository manifest:

- `k8s/tei.yaml`

From the jump server:

```bash
oc project <namespace>
oc apply -f k8s/tei.yaml
```

Verify that TEI pod is running:

```bash
oc get pods | grep tei
```

Check TEI logs (first startup may take time while downloading model weights):

```bash
oc logs deploy/customerllm-tei
```

You should see output indicating:

- the model is being downloaded/loaded
- the server is listening on port 8080

#### 4.3.3 Verify TEI API is reachable

Port-forward TEI service to verify endpoints:

```bash
oc port-forward svc/tei 8080:8080
```

Then open the docs endpoint:

```bash
curl http://localhost:8080/docs
```

If `/docs` returns HTML/JSON → TEI is running correctly.

#### 4.3.4 Test embeddings directly (Arabic text)

Run this test from the jump server (with port-forward active):

```bash
curl -X POST "http://localhost:8080/embed" \
  -H "Content-Type: application/json" \
  -d '{"inputs":["مرحبا","ما هي تفاصيل القضية؟"]}'
```

Expected result:

- A JSON response containing embedding vectors (arrays of floats).
- The vectors will be used by Qdrant for similarity search.

If this call fails:

- check logs: `oc logs deploy/customerllm-tei`
- confirm service endpoints: `oc describe svc tei`

#### 4.3.5 Configure the application to use TEI

In `.env.openshift` (used later when deploying the app), set:

```env
EMBEDDINGS_PROVIDER=tei
TEI_BASE_URL=http://tei:8080
TEI_API_TOKEN=
TEI_TIMEOUT=60
```

Notes:

- `TEI_API_TOKEN` is empty because TEI is used internally by the backend.
  (If you expose TEI externally via a route, you must secure it and populate this token.)

#### 4.3.6 Summary of Model Responsibilities

At the end of this section, the setup should be:

- **LLM (Chat):** OpenShift AI / vLLM Route (token-protected)
- **Embeddings:** TEI service inside cluster (`http://tei:8080`)

#### 4.3.7 Switching TEI Between CPU and GPUs

This project supports running the **TEI (Text Embeddings Inference)** service on either **CPU** or **GPU**, depending on the OpenShift cluster capabilities.

Two manifests are provided:

- `k8s/tei-cpu.yaml` → CPU-based embeddings
- `tei-gpu.yaml` → GPU-accelerated embeddings

Both manifests:

- Use the same Deployment name: `customerllm-tei`
- Use the same Service name: `tei`
- Expose TEI on port `8080`

This allows seamless switching by applying the desired manifest.

### When to Use CPU vs GPU

**Use CPU when:**

- No GPUs are available in the cluster
- This is a small-scale POC or demo
- Embedding throughput is low or moderate

**Use GPU when:**

- GPUs are available and allocated to your namespace
- Faster embedding generation is required
- You expect higher ingestion or query volume

### Check if GPUs Are Available

Before deploying the GPU variant, verify that GPU resources exist:

```bash
oc get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.status.allocatable.nvidia\.com/gpu}{"\n"}{end}'
```

If you see a number greater than `0`, GPU scheduling is available.

### Deploy TEI on CPU

Apply the CPU manifest:

```bash
oc apply -f k8s/tei-cpu.yaml
```

Verify:

```bash
oc get pods | grep tei
oc logs deploy/customerllm-tei
```

### Switch TEI to GPU

To switch from CPU to GPU, simply apply the GPU manifest:

```bash
oc apply -f tei-gpu.yaml
```

This will update the existing Deployment in place.

Verify:

```bash
oc get pods | grep tei
oc logs deploy/customerllm-tei
```

You should see logs indicating CUDA/GPU usage.

### Switch Back to CPU

To revert to CPU execution:

```bash
oc apply -f k8s/tei-cpu.yaml
```

### Important Notes

- Do **not** deploy both CPU and GPU manifests at the same time.
- The backend application does **not** need to be restarted when switching.
- The `TEI_BASE_URL` remains unchanged:

  ```env
  TEI_BASE_URL=http://tei:8080
  ```

- First startup may take several minutes while the model is downloaded.

---

### 4.4 Get Routes and Model IDs

```bash
oc get inferenceservices
oc get routes
```

You will obtain:

- LLM Route URL
- Embedding Route URL
- Model IDs (used later in env vars)

---

### 4.5 Test the Model Routes

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  https://<llm-route>/v1/models
```

If this returns model metadata → vLLM is ready.

---

## 5. Prepare Application Environment Configuration

Create the OpenShift environment file:

```bash
cp env.example .env.openshift
```

Edit `.env.openshift`:

```env
APP_ENV=production
DEBUG=false

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# vLLM (token-protected routes)
VLLM_BASE_URL=https://<llm-route>
VLLM_MODEL=<llm-model-id>
VLLM_EMBEDDING_BASE_URL=https://<embedding-route>
VLLM_EMBEDDING_MODEL=<embedding-model-id>
VLLM_API_TOKEN=<BEARER_TOKEN>

# Embeddings provider (TEI)
EMBEDDINGS_PROVIDER=tei
TEI_BASE_URL=http://tei:8080
TEI_API_TOKEN=
TEI_TIMEOUT=60

# Storage (PVC)
STORAGE_MODE=pvc
FILE_STORAGE_PATH=/data

# Vector DB
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION_NAME=documents

# Database
DATABASE_URL=postgresql://<user>:<pass>@postgres:5432/<db>
POSTGRES_DB=<db>
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<pass>

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=<32+ character random string>
```

---

## 6. Create OpenShift Secret

```bash
oc create secret generic customerllm-env \
  --from-env-file=.env.openshift
```

This secret injects **all configuration**, including the **vLLM token**, into the app.

---

## 7. Deploy the Application (Source Code)

Apply all manifests:

```bash
oc apply -f k8s/
```

This deploys:

- Backend
- Frontend
- OCR Worker
- Qdrant
- PostgreSQL
- Redis
- PVC for PDF storage
- TEI embeddings service

---

## 8. Verify PVC and Permissions

Check PVC status:

```bash
oc get pvc
```

Verify mount inside backend pod:

```bash
oc rsh deploy/customerllm-backend
ls -la /data
```

You should see a writable directory.

---

## 9. Verify vLLM Connectivity from the Application

```bash
oc rsh deploy/customerllm-backend
curl -H "Authorization: Bearer $VLLM_API_TOKEN" \
  $VLLM_BASE_URL/v1/models
```

If successful → backend can reach vLLM.

## 9a. Verify TEI

```
oc rsh deploy/customerllm-backend
curl http://tei:8080/docs
```

If docs respond → TEI is reachable.

---

## 10. Expose the Application

```bash
oc expose svc frontend
oc expose svc backend
oc get routes
```

Access:

- Frontend Route → UI
- Backend Route → API

---

## 11. End-to-End Validation Checklist

- [ ] All pods running
- [ ] PVC bound
- [ ] vLLM routes reachable
- [ ] PDFs upload successfully
- [ ] Files persist under `/data`
- [ ] OCR processes documents
- [ ] Chat answers returned
- [ ] Arabic/English language rules respected

---

## 12. Troubleshooting (Mandatory Reference)

### Pod CrashLoopBackOff

```bash
oc logs deploy/customerllm-backend
```

**Cause:** Missing env vars
**Fix:** Recreate secret with full `.env.openshift`

---

### Permission Denied on `/data`

**Cause:** PVC permissions
**Fix:** Ensure `fsGroup` or initContainer is set in manifests

---

### vLLM Returns 401 Unauthorized

**Cause:** Missing or invalid token
**Fix:** Check `VLLM_API_TOKEN` and header injection

---

### vLLM Route Unreachable

```bash
oc get routes
oc describe route <route-name>
```

**Cause:** Route not exposed or model not ready

---

### Embeddings Fail but Chat Works

**Cause:**

- TEI not running
- Wrong TEI_BASE_URL
- Wrong TEI endpoint path

**Fix:**

````bash
oc get pods | grep tei
oc logs deploy/customerllm-tei
oc rsh deploy/customerllm-backend
curl http://tei:8080/docs

---

### Health / Readiness Probe Fails

```bash
oc describe pod <pod>
````

**Cause:** App not bound to `0.0.0.0` or wrong probe path

---

## Final Notes

- Models are **managed by OpenShift AI**
- Application is **model-agnostic**
- Tokens are stored **only in Secrets**
- PVC guarantees PDF persistence
- This cookbook is sufficient to deploy the full system **from scratch**

---

**End of Cookbook**
