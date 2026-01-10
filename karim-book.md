Karim Deployment Playbook (Jump Server)

This is the exact flow to deploy the project from the jump server using the
manifests in `k8s/`. It assumes vLLM is already deployed in OpenShift AI and
you have its route + token.

Prereqs (once):
1) Install and verify tooling on the jump server:
   - `git --version`
   - `oc version`
   - `podman --version` (preferred) or `docker --version`

2) Clone the repo:
   - `git clone <repo-url>`
   - `cd <repo>`

3) Login and pick the namespace:
   - `oc login https://<cluster-api>:6443 --token=<TOKEN>`
   - `oc project <namespace>`

Step A: Configure vLLM + TEI in `.env.openshift`
1) Deploy vLLM in OpenShift AI and get:
   - vLLM Route URL
   - Model ID
   - Bearer token

2) Update `.env.openshift` placeholders:
   - `BACKEND_URL`, `FRONTEND_URL`, `VITE_API_URL`, `VITE_WS_URL`, `CORS_ORIGINS`
   - `POSTGRES_PASSWORD` and `DATABASE_URL`
   - `VLLM_BASE_URL`, `VLLM_MODEL`, `VLLM_API_TOKEN`
   - `VLLM_EMBEDDING_BASE_URL`, `VLLM_EMBEDDING_MODEL` (if using vLLM for embeddings)
   - `SECRET_KEY`

3) Confirm embeddings provider:
   - `EMBEDDINGS_PROVIDER=tei`
   - `TEI_BASE_URL=http://tei:8080`

Step B: Create the OpenShift secret
```
oc create secret generic customerllm-env --from-env-file=.env.openshift --dry-run=client -o yaml | oc apply -f -
```

Step C: Create build resources and build images
1) Create ImageStreams + BuildConfigs:
```
oc apply -f k8s/builds.yaml
```

2) Build images from the repo:
```
oc start-build customerllm-backend --from-dir=backend --follow
oc start-build customerllm-frontend --from-dir=frontend --follow
oc start-build customerllm-ocr-worker --from-dir=ocr-worker --follow
```

Step D: Deploy storage + core services
1) PVC + databases:
```
oc apply -f k8s/storage-pvc.yaml
oc apply -f k8s/postgres.yaml
oc apply -f k8s/redis.yaml
oc apply -f k8s/qdrant.yaml
```

2) TEI embeddings:
```
oc apply -f k8s/tei-cpu.yaml
```

Step E: Run DB migration + seed users (one time)
```
oc apply -f k8s/db-seed-job.yaml
oc wait --for=condition=complete job/customerllm-db-seed --timeout=300s
```

Step F: Deploy the app components
```
oc apply -f k8s/backend.yaml
oc apply -f k8s/ocr-worker.yaml
oc apply -f k8s/frontend.yaml
```

Step G: Point deployments to the built images
Replace `<namespace>` with your project name:
```
oc set image deploy/customerllm-backend backend=image-registry.openshift-image-registry.svc:5000/<namespace>/customerllm-backend:latest
oc set image deploy/customerllm-frontend frontend=image-registry.openshift-image-registry.svc:5000/<namespace>/customerllm-frontend:latest
oc set image deploy/customerllm-ocr-worker ocr-worker=image-registry.openshift-image-registry.svc:5000/<namespace>/customerllm-ocr-worker:latest
```

Step H: Expose routes and verify
```
oc expose svc customerllm-backend
oc expose svc customerllm-frontend
oc get routes
```

Verify health:
```
oc get pods
oc logs deploy/customerllm-backend
oc logs deploy/customerllm-ocr-worker
oc logs deploy/customerllm-tei
```

Notes / readiness checks:
- `k8s/storage-pvc.yaml` uses ReadWriteMany; ensure your storage class supports RWX.
- `k8s/tei-cpu.yaml` uses `intfloat/multilingual-e5-base` (768-dim).
- Backend uses Qdrant vector size 768, matching the TEI model output.
- vLLM must be reachable for `/ready` to pass.
