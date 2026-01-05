# Operations Runbook

## Daily Operations

### Health Checks

**Development:**
```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check Qdrant
curl http://localhost:6333/health

# Check OCR worker
curl http://localhost:8001/health
```

**Production:**
```bash
# Check all pods
kubectl get pods -n customerllm

# Check backend health
kubectl exec -it deployment/backend -n customerllm -- \
  curl http://localhost:8000/health

# View recent logs
kubectl logs --tail=100 deployment/backend -n customerllm
```

### Monitoring Dashboard

Access Grafana: http://localhost:3001 (admin/admin)

**Key Metrics to Monitor:**
- API request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database connections
- Qdrant vector count
- OCR processing time
- Celery queue length
- Memory usage per pod
- CPU usage per pod

### Alerts

**Critical Alerts** (immediate action):
- Service down (backend, Qdrant, database)
- Error rate > 5%
- Database connection pool exhausted
- Disk usage > 90%

**Warning Alerts** (investigate):
- High latency (p95 > 2s)
- Error rate > 1%
- Memory usage > 80%
- Qdrant response time > 500ms

## Backup & Restore

### Database Backup

**Manual Backup:**
```bash
# Development
docker-compose exec postgres pg_dump -U customerllm customerllm > backup_$(date +%Y%m%d).sql

# Production
kubectl exec -it deployment/postgres -n customerllm -- \
  pg_dump -U customerllm customerllm > backup_$(date +%Y%m%d).sql
```

**Automated Backup:**
Configure CronJob in Kubernetes:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: customerllm
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16-alpine
            command:
            - /bin/sh
            - -c
            - pg_dump -U customerllm -h postgres customerllm | gzip > /backups/backup_$(date +\%Y\%m\%d).sql.gz
            volumeMounts:
            - name: backups
              mountPath: /backups
          volumes:
          - name: backups
            persistentVolumeClaim:
              claimName: backups-pvc
          restartPolicy: OnFailure
```

**Restore:**
```bash
# Development
docker-compose exec -T postgres psql -U customerllm customerllm < backup.sql

# Production
kubectl exec -i deployment/postgres -n customerllm -- \
  psql -U customerllm customerllm < backup.sql
```

### Qdrant Backup

**Create Snapshot:**
```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/documents/snapshots

# List snapshots
curl http://localhost:6333/collections/documents/snapshots

# Download snapshot
curl http://localhost:6333/collections/documents/snapshots/<snapshot_name> \
  -o qdrant_backup_$(date +%Y%m%d).tar
```

**Restore Snapshot:**
```bash
# Upload and restore
curl -X PUT http://localhost:6333/collections/documents/snapshots/upload \
  -H "Content-Type: multipart/form-data" \
  -F "snapshot=@qdrant_backup.tar"
```

### Object Storage Backup

**MinIO:**
```bash
# Install mc (MinIO Client)
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Configure
mc alias set myminio http://localhost:9000 minioadmin minioadmin_password

# Backup
mc mirror myminio/customerllm /backups/minio/$(date +%Y%m%d)
```

## Common Issues & Solutions

### Backend Won't Start

**Issue:** Backend pod in CrashLoopBackOff

**Investigation:**
```bash
kubectl logs deployment/backend -n customerllm
kubectl describe pod <backend-pod> -n customerllm
```

**Common Causes:**
1. Database connection failure
   - Check database is running
   - Verify DATABASE_URL secret
   - Check network policy

2. Missing migrations
   ```bash
   kubectl exec -it deployment/backend -n customerllm -- \
     alembic upgrade head
   ```

3. Missing secrets
   ```bash
   kubectl get secrets -n customerllm
   kubectl describe secret customerllm-secrets -n customerllm
   ```

### Qdrant Connection Issues

**Symptoms:** Search fails, vector upsert fails

**Investigation:**
```bash
# Check Qdrant health
kubectl exec -it deployment/qdrant -n customerllm -- \
  curl http://localhost:6333/health

# Check collections
kubectl exec -it deployment/qdrant -n customerllm -- \
  curl http://localhost:6333/collections
```

**Solutions:**
1. Restart Qdrant
   ```bash
   kubectl rollout restart deployment/qdrant -n customerllm
   ```

2. Recreate collection
   ```bash
   # Delete collection
   curl -X DELETE http://localhost:6333/collections/documents
   
   # Restart backend (will recreate collection)
   kubectl rollout restart deployment/backend -n customerllm
   ```

### OCR Processing Fails

**Symptoms:** Documents stuck in "OCR_PROCESSING" status

**Investigation:**
```bash
# Check OCR worker logs
kubectl logs deployment/ocr-worker -n customerllm

# Check document status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/admin/documents/<doc_id>/status
```

**Solutions:**
1. Restart OCR worker
   ```bash
   kubectl rollout restart deployment/ocr-worker -n customerllm
   ```

2. Retry OCR processing
   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/admin/documents/<doc_id>/process-ocr
   ```

3. Check Ollama connection
   ```bash
   kubectl exec -it deployment/ollama -n customerllm -- \
     curl http://localhost:11434/api/tags
   ```

### High Memory Usage

**Investigation:**
```bash
# Check pod memory
kubectl top pods -n customerllm

# Check container metrics
kubectl exec -it deployment/backend -n customerllm -- \
  ps aux --sort=-%mem | head -10
```

**Solutions:**
1. Increase resource limits in deployment
2. Reduce worker concurrency
3. Enable memory profiling:
   ```python
   import memory_profiler
   @profile
   def my_function():
       pass
   ```

4. Check for memory leaks:
   ```bash
   # Install py-spy
   pip install py-spy
   
   # Profile running process
   py-spy top --pid <pid>
   ```

### Database Connection Pool Exhausted

**Symptoms:** "connection pool exhausted" errors

**Investigation:**
```bash
# Check active connections
docker-compose exec postgres psql -U customerllm -c \
  "SELECT count(*) FROM pg_stat_activity;"
```

**Solutions:**
1. Increase pool size in `app/core/config.py`:
   ```python
   DB_POOL_SIZE: int = 40
   DB_MAX_OVERFLOW: int = 80
   ```

2. Check for connection leaks:
   ```python
   # Ensure sessions are closed
   db = SessionLocal()
   try:
       # ... operations
   finally:
       db.close()
   ```

3. Restart backend:
   ```bash
   kubectl rollout restart deployment/backend -n customerllm
   ```

## Scaling Operations

### Scale Backend

```bash
# Manual scale
kubectl scale deployment backend --replicas=10 -n customerllm

# Auto-scale (HPA already configured)
kubectl get hpa -n customerllm
kubectl describe hpa backend-hpa -n customerllm
```

### Scale Database

**Vertical Scaling:**
1. Update resource limits in `postgres.yaml`
2. Apply changes:
   ```bash
   kubectl apply -f infrastructure/kubernetes/postgres.yaml
   ```

**Horizontal Scaling (Read Replicas):**
1. Set up PostgreSQL streaming replication
2. Configure read-only replicas
3. Update application to use read replicas for queries

### Scale Qdrant

For large vector databases:
1. Use Qdrant Cloud (managed service)
2. Or configure Qdrant cluster with sharding
3. Consider using Qdrant's distributed mode

## Disaster Recovery

### Complete System Failure

**Recovery Steps:**
1. Restore infrastructure (Kubernetes cluster)
2. Apply all manifests:
   ```bash
   kubectl apply -f infrastructure/kubernetes/
   ```
3. Restore database:
   ```bash
   kubectl exec -i deployment/postgres -n customerllm -- \
     psql -U customerllm customerllm < backup.sql
   ```
4. Restore Qdrant:
   ```bash
   curl -X PUT http://localhost:6333/collections/documents/snapshots/upload \
     -F "snapshot=@qdrant_backup.tar"
   ```
5. Restore MinIO data:
   ```bash
   mc mirror /backups/minio/latest myminio/customerllm
   ```
6. Verify all services:
   ```bash
   kubectl get pods -n customerllm
   curl http://<domain>/api/v1/health
   ```

### Data Corruption

1. Stop affected services
2. Restore from last known good backup
3. Replay transaction logs if available
4. Verify data integrity
5. Resume services

## Maintenance Windows

### Database Maintenance

**Minor Updates:**
```bash
# Update PostgreSQL image
kubectl set image deployment/postgres \
  postgres=postgres:16.1-alpine -n customerllm

# Rollout
kubectl rollout status deployment/postgres -n customerllm
```

**Major Migrations:**
1. Schedule maintenance window
2. Notify users
3. Create backup
4. Run migrations:
   ```bash
   kubectl exec -it deployment/backend -n customerllm -- \
     alembic upgrade head
   ```
5. Verify application
6. Resume operations

### Certificate Rotation

**TLS Certificates:**
```bash
# Check expiry
kubectl get certificate -n customerllm

# Cert-manager auto-renews, but to force:
kubectl delete certificate customerllm-tls -n customerllm
# Cert-manager will recreate
```

**JWT Secret Rotation:**
1. Generate new secret
2. Update secret in Kubernetes
3. Gradual rollout (keep old key for grace period)
4. Remove old key after grace period

## Performance Tuning

### Database Optimization

**Index Management:**
```sql
-- List missing indexes
SELECT schemaname, tablename, attname
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
AND n_distinct > 100
ORDER BY n_distinct DESC;

-- Add indexes as needed
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
```

**Query Optimization:**
```bash
# Enable query logging
docker-compose exec postgres psql -U customerllm -c \
  "ALTER SYSTEM SET log_min_duration_statement = 100;"

# Restart to apply
docker-compose restart postgres
```

### Qdrant Optimization

**Index Configuration:**
```python
# Optimize for speed
client.update_collection(
    collection_name="documents",
    optimizer_config=OptimizersConfigDiff(
        indexing_threshold=10000,
    )
)

# Optimize HNSW parameters
client.update_collection(
    collection_name="documents",
    hnsw_config=HnswConfigDiff(
        m=32,
        ef_construct=200,
    )
)
```

## Logging

### Centralized Logging (ELK/OpenSearch)

**Ship Logs:**
```yaml
# Filebeat DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: filebeat
  namespace: customerllm
spec:
  template:
    spec:
      containers:
      - name: filebeat
        image: elastic/filebeat:8.11.0
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
```

### Log Queries

**Find Errors:**
```bash
# Kubernetes
kubectl logs -l app=backend -n customerllm --tail=1000 | grep ERROR

# OpenSearch
GET /logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" }},
        { "range": { "@timestamp": { "gte": "now-1h" }}}
      ]
    }
  }
}
```

## Contact Information

- **On-Call Engineer**: +1-XXX-XXX-XXXX
- **DevOps Team**: devops@example.com
- **Security Team**: security@example.com
- **Management**: management@example.com

## Escalation Path

1. **Level 1**: On-call engineer
2. **Level 2**: Team lead
3. **Level 3**: Engineering manager
4. **Level 4**: CTO

## References

- [API Documentation](./API.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Security Guidelines](./SECURITY.md)
- Kubernetes Dashboard: https://k8s.example.com
- Grafana: https://grafana.example.com
- OpenSearch: https://logs.example.com

