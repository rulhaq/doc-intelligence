#!/bin/sh
set -eu

# In Kubernetes/OpenShift, run migrations and seeding via the dedicated Job
# (`k8s/db-seed-job.yaml`). Keep the API startup fast by default.
if [ "${WAIT_FOR_DB:-false}" = "true" ]; then
  python - <<'PY'
import os
import time
import psycopg2

dsn = os.environ.get("DATABASE_URL")
if not dsn:
    raise SystemExit("DATABASE_URL is not set")

for attempt in range(60):
    try:
        conn = psycopg2.connect(dsn)
        conn.close()
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time")
PY
fi

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  alembic upgrade head
fi

if [ "${SEED_USERS:-false}" = "true" ]; then
  python scripts/seed_users.py
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT}" --workers "${UVICORN_WORKERS:-4}"
