# OpenShift AI Deployment Cookbook (UI / Web Console)

This cookbook deploys the **current QPP-PoC codebase** using the YAMLs in `new-deployment/`.

It assumes:
- You deploy into a single OpenShift **Project/Namespace**.
- `quay-push-secret` **already exists** in that Project (for pushing/pulling images).
- The **LLM service already exists** in the client environment (do **not** redeploy it here). You will only reference its internal/external endpoints in `new-deployment/qpp-config.yaml`.

---

## Contents
- [1. Prepare values (edit manifests)](#1-prepare-values-edit-manifests)
- [2. Create / select project](#2-create--select-project)
- [3. Apply YAMLs (in the correct order)](#3-apply-yamls-in-the-correct-order)
- [4. Start builds (UI)](#4-start-builds-ui)
- [5. Deploy backend + frontend](#5-deploy-backend--frontend)
- [6. Seed login users (admin + user)](#6-seed-login-users-admin--user)
- [7. Validate end-to-end](#7-validate-end-to-end)
- [8. Troubleshooting checklist](#8-troubleshooting-checklist)

---

## 1. Prepare values (edit manifests)

Before importing anything into OpenShift, update these local files:

### 1.1 Update Git source (required)
File: `new-deployment/builds-client.yaml`

Edit both BuildConfigs:
- `spec.source.git.uri` → your real Git repo URL
- `spec.source.git.ref` → branch/tag/commit to build (example: `main`)

### 1.2 Update secrets (required)
File: `new-deployment/qpp-secrets.yaml`

Set real values (do **not** keep placeholders):
- `POSTGRES_PASSWORD`
- `DATABASE_URL` (must match the Postgres service name `postgres` and the credentials)
- `SECRET_KEY` (use a long random string; 32+ chars recommended)

Seed users for first login (used by the DB seed job):
- `SEED_ADMIN_USERNAME`, `SEED_ADMIN_PASSWORD`
- `SEED_USER_USERNAME`, `SEED_USER_PASSWORD`

Optional tokens (only if your endpoints require them):
- `VLLM_API_KEY`
- `TEI_API_KEY`

### 1.3 Update config (required)
File: `new-deployment/qpp-config.yaml`

Confirm or change:
- **LLM endpoints** (LLM already deployed; reference only):
  - `VLLM_BASE_URL` (internal, in-cluster)
  - `VLLM_BASE_URL_FALLBACK` (external/route)
  - `VLLM_MODEL` (must match what the OpenAI-compatible endpoint expects)
  - `VLLM_TLS_VERIFY` (keep `"true"` unless you *must* disable verification)
- **TEI embeddings**:
  - `TEI_BASE_URL` should be `http://tei:8080` (matches `tei-cpu-client.yaml`)
- **Qdrant**:
  - `QDRANT_HOST=qdrant`, `QDRANT_PORT=6333` (matches `qdrant-client.yaml`)

### 1.4 Confirm storage class
Files:
- `new-deployment/storage-pvc-client.yaml`
- `new-deployment/postgre-client.yaml`
- `new-deployment/qdrant-client.yaml`

Ensure `storageClassName: genai-sc` is valid in your cluster. If your cluster uses a different StorageClass, change it consistently across those files.

---

## 2. Create / select project

In the OpenShift Web Console:
1. Switch to **Administrator** (top-left perspective dropdown).
2. Open the **Project** dropdown (top bar).
3. Either:
   - **Create Project** (example name: `qpp-poc`), or
   - Select an existing Project where you will deploy everything.

All YAML imports below must be done in the same Project.

---

## 3. Apply YAMLs (in the correct order)

You will import YAMLs via the UI:
1. Go to **+Add** (left nav).
2. Click **Import YAML**.
3. Paste the file contents (or upload the file if supported).
4. Click **Create**.

Apply in this **exact order** (matches `new-deployment/README.md`):

1) `new-deployment/qpp-secrets.yaml`  
2) `new-deployment/qpp-config.yaml`  
3) `new-deployment/storage-pvc-client.yaml`  
4) `new-deployment/postgre-client.yaml`  
5) `new-deployment/qdrant-client.yaml`  
6) `new-deployment/tei-cpu-client.yaml`  
7) `new-deployment/builds-client.yaml`  
8) Start builds (next section)  
9) `new-deployment/backend-client.yaml`  
10) `new-deployment/frontend-client.yaml`  
11) (Optional) `new-deployment/db-seed-job-client.yaml`  

Notes:
- Steps 4–6 deploy **dependencies** (Postgres, Qdrant, TEI). If your client environment already provides any of these as managed services, you can skip their YAML and adjust `qpp-config.yaml` / `qpp-secrets.yaml` to point to the managed services.
- Step 7 creates BuildConfigs + ImageStreams; deployments in steps 9–10 pull from the external registry image references and also include ImageStream triggers.

---

## 4. Start builds (UI)

After applying `new-deployment/builds-client.yaml`:

1. Go to **Builds → BuildConfigs**.
2. Open `qpp-backend`.
3. Click **Actions → Start Build**.
4. Watch logs:
   - **Builds → Builds** → open the running build → **Logs** tab.
5. Repeat for `qpp-frontend`.

Wait until both builds are **Complete** before proceeding.

If builds fail, fix the code or BuildConfig settings, then start a new build.

---

## 5. Deploy backend + frontend

After the builds complete, apply:
- `new-deployment/backend-client.yaml`
- `new-deployment/frontend-client.yaml`

### 5.1 Verify pods are running
Go to **Workloads → Deployments**:
- `qpp-backend` should show **1 available** replica.
- `qpp-frontend` should show **1 available** replica.

If a pod is crashing:
- click the pod → **Logs**
- click the pod → **Events**

### 5.2 Verify routes exist
Go to **Networking → Routes**:
- `qpp-frontend` (primary UI entry)
- `qpp-backend` (optional direct API access)

Open the `qpp-frontend` route in your browser.

---

## 6. Seed login users (admin + user)

This is how you get initial credentials in Postgres so people can log in.

1. Confirm you set these in `new-deployment/qpp-secrets.yaml`:
   - `SEED_ADMIN_USERNAME`, `SEED_ADMIN_PASSWORD`
   - `SEED_USER_USERNAME`, `SEED_USER_PASSWORD`
2. Apply `new-deployment/db-seed-job-client.yaml`.
3. Go to **Workloads → Jobs** → `qpp-db-seed`.
4. Open the Job logs:
   - You should see either “User created …” or “User already exists …”.

Re-running the job:
- Jobs do not re-run automatically after completion.
- To re-run, delete the Job in the UI and import the YAML again.

---

## 7. Validate end-to-end

### 7.1 Frontend loads
- Open the `qpp-frontend` Route URL in a browser.

### 7.2 Backend health and docs
Either:
- open the `qpp-backend` Route URL and visit:
  - `/health`
  - `/docs`
or (recommended):
- open the `qpp-frontend` Route URL and visit:
  - `/health` (proxied to backend)
  - `/docs` (proxied to backend)

### 7.3 Login
- Login using the admin/user credentials you configured in `new-deployment/qpp-secrets.yaml`.

### 7.4 Functional checks
- TEI embeddings: chat/intelligence endpoints should not error when embedding is needed.
- Qdrant: document upload + retrieval should work.
- LLM: responses should come from the existing OpenShift AI LLM endpoint (internal first, external fallback if configured).

---

## 8. Troubleshooting checklist

### Builds
- **Build fails cloning repo**: `builds-client.yaml` git `uri/ref` wrong or credentials needed.
- **Frontend build fails**: check frontend Dockerfile and `package-lock.json` are in sync.
- **Backend build fails**: check Python deps and Dockerfile.

### Image pull / registry auth
- Pod events show `ImagePullBackOff`: verify `quay-push-secret` exists in the Project and is referenced by the Deployments (it is in the YAMLs).

### Backend can’t connect to DB
- Check `DATABASE_URL` in `qpp-secrets.yaml` points to:
  - host `postgres`
  - port `5432`
  - db/user/password match your postgres envs
- Check postgres pod is running and Service `postgres` exists.

### Backend can’t call LLM
- Confirm `VLLM_BASE_URL` is reachable from the backend pod.
- If using an internal HTTPS service with a private CA, you may need:
  - set `VLLM_TLS_VERIFY` to `"false"` (temporary), or
  - mount the CA bundle and set `VLLM_CA_BUNDLE` (preferred, if you implement CA mounting).

### Frontend loads but API calls fail
- Ensure backend Service is named `qpp-backend`.
- Ensure nginx proxy is sending `/api/*` to `http://qpp-backend/api/` (this is in the built frontend image).
- Check backend pod logs for auth errors / missing env vars.

---

## Quick reference: files used
- Secrets: `new-deployment/qpp-secrets.yaml`
- Config: `new-deployment/qpp-config.yaml`
- PVC (documents): `new-deployment/storage-pvc-client.yaml`
- Postgres: `new-deployment/postgre-client.yaml`
- Qdrant: `new-deployment/qdrant-client.yaml`
- TEI: `new-deployment/tei-cpu-client.yaml`
- Builds: `new-deployment/builds-client.yaml`
- Backend app: `new-deployment/backend-client.yaml`
- Frontend app: `new-deployment/frontend-client.yaml`
- Seed users job: `new-deployment/db-seed-job-client.yaml`

