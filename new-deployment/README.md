# new-deployment/

These manifests recreate the **same apply sequence** used in `old-deployment/`, updated for the **current QPP-PoC codebase**.

## Apply order

1) `qpp-secrets.yaml` (required)
2) `qpp-config.yaml`
3) `storage-pvc-client.yaml`
4) `postgre-client.yaml`
5) `qdrant-client.yaml`
6) `tei-cpu-client.yaml`
7) `builds-client.yaml` (BuildConfigs + ImageStreams)
8) Start builds:
   - `oc start-build qpp-backend --follow`
   - `oc start-build qpp-frontend --follow`
9) `backend-client.yaml`
10) `frontend-client.yaml`
11) Optional: `db-seed-job-client.yaml`

## Notes

- LLM (vLLM) is **not deployed here**. Set `VLLM_BASE_URL` (and optional fallback) in `qpp-config.yaml`.
- `quay-push-secret` is assumed to already exist for BuildConfig push + image pulls.
- The optional DB seed job creates 2 login users from `qpp-secrets.yaml`: `SEED_ADMIN_USERNAME/SEED_ADMIN_PASSWORD` and `SEED_USER_USERNAME/SEED_USER_PASSWORD`.
