# Security Guidelines

## Authentication & Authorization

### Token Management
- Access tokens expire after 30 minutes (configurable)
- Refresh tokens expire after 7 days (configurable)
- Tokens are JWT-based with HS256 algorithm
- Store tokens securely (httpOnly cookies recommended for production)

### Password Requirements
- Minimum 8 characters
- Passwords are hashed with bcrypt
- No plaintext passwords stored
- Password reset flow should be implemented

### Role-Based Access Control (RBAC)

**Roles:**
- **Admin**: Full access (all endpoints, user management, document management)
- **Editor**: Can edit documents, create agents, use chat
- **Viewer**: Read-only access to chat and documents

**Enforcement:**
- Backend validates roles on every request
- Frontend hides UI elements based on role
- API endpoints protected with `require_role()` dependency

## API Security

### Rate Limiting
- Configured per endpoint
- Default: 60 requests/minute, 1000 requests/hour
- Adjust in `app/core/config.py`

### CORS
- Configure allowed origins in `.env`
- Default: `http://localhost:3000,http://localhost:5173`
- Production: Set to your actual domain

### Input Validation
- All inputs validated with Pydantic models
- SQL injection protection via SQLAlchemy ORM
- File upload validation (size, type, content)

### File Upload Security
- Max file size: 100MB (configurable)
- Allowed extensions: PDF, DOCX, TXT only
- Files stored with UUID names
- Virus scanning recommended (add ClamAV)

## Data Encryption

### At Rest
- Database: Enable PostgreSQL encryption
- Object Storage: Enable MinIO/S3 server-side encryption
- Qdrant: Enable encryption at rest
- Sensitive data: Encrypt with Fernet (configured in `.env`)

### In Transit
- TLS 1.3 for all HTTP traffic
- Configure SSL certificates (Let's Encrypt recommended)
- Ingress termination for Kubernetes

## Secrets Management

### Development
- Use `.env` file (DO NOT commit to git)
- `.env.example` for reference only

### Production
- **Recommended:** Use external secrets manager
  - Azure Key Vault
  - AWS Secrets Manager
  - HashiCorp Vault
  - Kubernetes External Secrets Operator

- **Kubernetes Secrets:**
  ```bash
  kubectl create secret generic customerllm-secrets \
    --from-literal=... \
    -n customerllm
  ```

### Secrets to Manage
- Database credentials
- Redis password
- Secret key (32+ characters)
- OAuth client secrets
- S3/MinIO credentials
- API keys for external services

## Network Security

### DMZ Architecture
For internet-enabled agents:

```
┌─────────────────────────────────────────┐
│              Internet                    │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────▼─────────┐
         │    DMZ Zone       │
         │  (Agent Workers)  │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │  Internal Network │
         │  (Backend, DB)    │
         └───────────────────┘
```

### Network Policies
Apply Kubernetes Network Policies:
- Deny all by default
- Allow only required traffic
- Isolate database, Qdrant, Redis

## Audit Logging

### What to Log
- All authentication attempts (success/failure)
- Admin actions (document upload, commit, delete)
- Agent execution
- Document access
- Permission changes

### Log Storage
- Logs stored in `audit_logs` table
- Optional: Ship to OpenSearch/ELK
- Retention: 365 days (configurable)

### Example Audit Log
```json
{
  "user_id": "uuid",
  "username": "admin@example.com",
  "action": "document.commit",
  "resource_type": "document",
  "resource_id": "doc-uuid",
  "ip_address": "10.0.1.5",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## PII & Data Protection

### PII Detection
- Enable `PII_REDACTION_ENABLED=true`
- Automatically redact emails, phone numbers, SSNs
- Use NER models for advanced detection

### Data Retention
- Configure `DATA_RETENTION_DAYS` (default: 365)
- Implement purge scripts for old data
- Provide data export API for users

### GDPR Compliance
- Right to access: Export user data
- Right to erasure: Delete user and associated data
- Data portability: JSON export format

## Vulnerability Management

### Dependency Scanning
```bash
# Backend
pip install safety
safety check -r backend/requirements.txt

# Frontend
npm audit
```

### Container Scanning
- Scan Docker images with Trivy
- Use minimal base images (Alpine)
- Keep images updated

### Penetration Testing
- Regular security audits
- OWASP Top 10 testing
- API fuzzing

## Incident Response

### Security Incident Checklist
1. **Detect**: Monitor logs, alerts
2. **Contain**: Disable compromised accounts, isolate affected systems
3. **Investigate**: Review audit logs, access patterns
4. **Remediate**: Patch vulnerabilities, rotate secrets
5. **Document**: Incident report, lessons learned

### Emergency Contacts
- Security team email
- On-call rotation
- External security consultant

## Compliance

### ISO 27001
- Information security management system (ISMS)
- Risk assessment and treatment
- Security policies and procedures

### SOC 2
- Security controls documentation
- Regular audits
- Continuous monitoring

### Regional Compliance
- Qatar: National Cybersecurity Framework
- EU: GDPR
- US: HIPAA (if handling health data)

## Security Checklist

### Deployment Security
- [ ] Change all default passwords
- [ ] Generate secure SECRET_KEY (32+ characters)
- [ ] Enable TLS/HTTPS everywhere
- [ ] Configure network policies
- [ ] Enable audit logging
- [ ] Set up RBAC properly
- [ ] Use secrets manager
- [ ] Enable pod security policies
- [ ] Configure resource limits
- [ ] Scan container images
- [ ] Enable disk encryption
- [ ] Configure backup encryption
- [ ] Set up monitoring and alerting
- [ ] Test disaster recovery
- [ ] Document security procedures

### Application Security
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (ORM)
- [ ] XSS protection (Content Security Policy)
- [ ] CSRF protection (SameSite cookies)
- [ ] Rate limiting enabled
- [ ] File upload validation
- [ ] Password complexity requirements
- [ ] Multi-factor authentication (optional)
- [ ] Session management
- [ ] Secure error handling (no stack traces)

### Infrastructure Security
- [ ] Firewall rules configured
- [ ] VPN for admin access
- [ ] SSH key authentication only
- [ ] Bastion host for database access
- [ ] Log aggregation (ELK/OpenSearch)
- [ ] Intrusion detection system (IDS)
- [ ] DDoS protection
- [ ] Regular security patches
- [ ] Vulnerability scanning
- [ ] Security training for team

## Security Contacts

Report security vulnerabilities to: security@example.com

**Do not** disclose security issues publicly until patched.

