Reve Deployment Book (OpenShift UI)

Goal: deploy the POC from branch `vllm-redhat-qpp-poc` using OpenShift _UI only_ (no local Docker/Podman). This deploys:

- Postgres + Redis + Qdrant + TEI
- Backend + Frontend + OCR Worker (built inside OpenShift using BuildConfigs)
- One-time DB migration + seed users job

What was fixed in the repo/manifests (so it works on OpenShift restricted SCC)

- **SCC / random UID**: manifests use `fsGroup` from the project supplemental range (no fixed `1000`).
- **Postgres initdb**: uses `PGDATA=/var/lib/postgresql/data/pgdata` to avoid `lost+found` mount issues.
- **Qdrant permissions**: writable temp/snapshots paths fixed so it can run under restricted SCC.
- **TEI permissions**: cache dirs moved to writable paths so it can download the embedding model.
- **OCR worker permissions**: PaddleOCR cache redirected to `/data` (PVC) so model downloads work.
- **Frontend nginx on OpenShift**:
  - `config.js` is generated at startup and is **not cached** (prevents stale API URL issues).
  - nginx temp dirs moved to `/tmp` (works with random UID).
- **vLLM is optional**: backend doesn’t crash if vLLM returns 401/403 when token isn’t set (it logs warnings only).
- **Embeddings + vector DB verified**: TEI (8080) → embeddings → Qdrant upsert works (768-dim).
- **Routes are HTTPS**: `k8s/frontend.yaml` + `k8s/backend.yaml` include edge-terminated Routes.

Important: namespace-specific `fsGroup`

- Every OpenShift project has an allowed supplemental group range.
- In the UI, find it via Project details/annotations, or ask an admin.
- If deploying into a different namespace than the sandbox used during testing, update `fsGroup` values in these files to match that namespace:
  - `k8s/postgres.yaml`
  - `k8s/qdrant.yaml`
  - `k8s/tei-cpu.yaml`
  - `k8s/backend.yaml`
  - `k8s/ocr-worker.yaml`

1. Import the repo (UI)

1) Open OpenShift Console → **Developer** perspective.
2) Click **+Add** → **Import from Git**.
3) Git Repo URL: `https://github.com/rulhaq/doc-intelligence.git`
4) Advanced Git options → set **Git reference** to `vllm-redhat-qpp-poc`.
5) Create an application (name it something like `customerllm`).

Note: Import-from-Git is mainly to connect the repo in the UI. The actual deployment uses the YAML in `k8s/`.

2. Create the environment secret (UI)
   This deployment expects a Secret named `customerllm-env` with all env vars from `.env.openshift`.

1) In the repo, open `.env.openshift` and set:
   - `BACKEND_URL` (backend route, once created)
   - `FRONTEND_URL` (frontend route, once created)
   - `VITE_API_URL` (must match backend route)
   - `VITE_WS_URL` (must match backend route, `wss://...`)
   - `CORS_ORIGINS` (must match frontend route, no trailing slash)
   - `POSTGRES_PASSWORD` + `DATABASE_URL` (keep consistent)
   - `SECRET_KEY` (random 32+ chars)
2) In OpenShift UI: **Workloads → Secrets → Create → Key/value secret**
3) Name: `customerllm-env`
4) Use “Upload” / “From file” (if available) and provide `.env.openshift`,
   otherwise paste the key/values.

3. Deploy stateful dependencies (UI → Import YAML)
   Apply these first (order matters):

1) `k8s/storage-pvc.yaml`
2) `k8s/postgres.yaml`
3) `k8s/redis.yaml`
4) `k8s/qdrant.yaml`
5) `k8s/tei-cpu.yaml`

In the UI: **+Add → Import YAML** and paste each file’s contents.

Wait until these pods are Running/Ready:

- postgres
- redis
- qdrant
- tei

4. Create BuildConfigs (UI) and build images
   The repo includes `k8s/builds.yaml` which creates ImageStreams + BuildConfigs.

1) UI → **+Add → Import YAML** → apply `k8s/builds.yaml`
2) UI → **Builds → BuildConfigs**
3) For each BuildConfig (`customerllm-backend`, `customerllm-frontend`, `customerllm-ocr-worker`), edit it in the UI:
   - Change source from `Binary` to `Git`
   - Set:
     - Git URL: `https://github.com/rulhaq/doc-intelligence.git`
     - Git ref: `vllm-redhat-qpp-poc`
     - Context dir:
       - backend: `backend`
       - frontend: `frontend`
       - ocr worker: `ocr-worker`
     - Dockerfile path: `Dockerfile`
4) Start builds from the UI (Builds → select BuildConfig → Start Build) for:
   - backend
   - frontend
   - ocr-worker

Wait until all 3 builds complete successfully.

5. Run DB migrations + seed users (one-time)
   Run this once _after_:

- Postgres is Running, and
- the backend image has been built (the seed job uses the backend image).

1. UI → **+Add → Import YAML** → apply `k8s/db-seed-job.yaml`
2. Wait for the Job `customerllm-db-seed` to reach **Complete**.

Seeded credentials (as configured in `.env.openshift` during the POC):

- admin / admin123456
- user / user123456

6. Deploy app components (UI → Import YAML)
   Apply:

1) `k8s/backend.yaml`
2) `k8s/ocr-worker.yaml`
3) `k8s/frontend.yaml`

7. Routes (HTTPS) and final checks
   Routes are defined in:

- `k8s/frontend.yaml` (Route `customerllm-frontend`, edge TLS)
- `k8s/backend.yaml` (Route `customerllm-backend`, edge TLS)

After applying, go to **Networking → Routes** and copy:

- Frontend URL → open in browser
- Backend URL → optional sanity check: `/health` and `/ready`

Verify in the UI:

1. Login works (admin/user)
2. Upload PDF
3. OCR runs
4. Commit stores vectors in Qdrant

LLM/vLLM notes (client environment)

- vLLM route can return 401/403 if a token is required.
- This repo is configured so the backend still runs without the token (it logs warnings and skips blocking startup).
- When the client provides token + model id:
  - set `VLLM_API_TOKEN` and `VLLM_MODEL` in `customerllm-env`
  - optionally set `VLLM_HEALTHCHECK_STRICT=true` to enforce startup readiness on vLLM.
