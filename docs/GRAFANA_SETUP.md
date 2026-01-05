# Grafana Dashboard Setup Guide

This guide explains how to access and use the Grafana monitoring dashboards for CustomerLLM.

## 🔗 Quick Access

### Grafana Dashboard
- **URL:** http://localhost:3001
- **Username:** `admin`
- **Password:** `admin` (change this in production!)
- **Dashboard Name:** CustomerLLM - Application Monitoring

### Other Monitoring Tools
- **Prometheus:** http://localhost:9090
- **Qdrant Dashboard:** http://localhost:6333/dashboard
- **MinIO Console:** http://localhost:9001

## 📊 Dashboard Overview

The CustomerLLM dashboard provides comprehensive monitoring with the following panels:

### 1. **Total Requests**
- Shows the cumulative number of HTTP requests
- Real-time counter that updates every 30 seconds

### 2. **Request Rate by Endpoint**
- Line graph showing requests per second
- Broken down by HTTP method and endpoint
- Helps identify traffic patterns and popular endpoints

### 3. **Response Time (p95)**
- 95th percentile response time
- Single stat showing current performance
- Color-coded thresholds:
  - Green: < 0.5s
  - Yellow: 0.5s - 1s
  - Red: > 1s

### 4. **Response Time Distribution**
- Shows p50, p95, and p99 response times
- Helps identify performance bottlenecks
- Tracks trends over time

### 5. **Error Rate (5xx)**
- Percentage of server errors
- Color-coded thresholds:
  - Green: 0%
  - Yellow: 1-5%
  - Red: > 5%

### 6. **Client Error Rate (4xx)**
- Percentage of client errors (bad requests)
- Useful for identifying API misuse

### 7. **HTTP Status Codes**
- Stacked area chart showing distribution of status codes
- Helps identify error patterns

### 8. **Memory Usage**
- Backend process memory consumption
- Useful for detecting memory leaks

### 9. **CPU Usage**
- Backend CPU utilization
- Helps with capacity planning

### 10. **Top 10 Endpoints**
- Table showing most frequently accessed endpoints
- Includes method, status, and request rate

## 🚀 Getting Started

### Step 1: Ensure Services are Running

```powershell
# Check service status
docker compose ps

# All services should show "Up" and "healthy"
```

### Step 2: Generate Traffic for Testing

```powershell
# Run the traffic generation script
.\scripts\generate-traffic.ps1

# Or manually make requests
for ($i=0; $i -lt 20; $i++) { 
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | Out-Null
    Start-Sleep -Milliseconds 100
}
```

### Step 3: Access Grafana

1. Open your browser and navigate to http://localhost:3001
2. Log in with credentials: `admin` / `admin`
3. You'll see the Grafana home page
4. Click on "Dashboards" in the left sidebar
5. Select "CustomerLLM - Application Monitoring"

### Step 4: Explore the Dashboard

- Use the time range selector (top right) to view different time periods
- Click on panel titles to expand them
- Hover over graphs to see detailed values
- Use the refresh dropdown to change auto-refresh interval

## 📈 Understanding Metrics

### Prometheus Metrics

The backend exposes the following metrics at `/metrics`:

- `http_requests_total` - Counter of HTTP requests
- `http_request_duration_seconds` - Histogram of request durations
- `process_resident_memory_bytes` - Memory usage
- `process_cpu_seconds_total` - CPU usage
- And many more standard Python/FastAPI metrics

### Custom Metrics

You can add custom metrics in the backend code:

```python
from prometheus_client import Counter, Histogram

# Define custom metrics
custom_counter = Counter('my_custom_counter', 'Description')
custom_histogram = Histogram('my_custom_duration', 'Description')

# Use in your code
custom_counter.inc()
with custom_histogram.time():
    # Your code here
    pass
```

## 🔧 Customization

### Modifying the Dashboard

1. Open the dashboard in Grafana
2. Click the gear icon (⚙️) at the top
3. Select "Settings"
4. Make your changes
5. Click "Save dashboard"

### Adding New Panels

1. Click "Add" → "Visualization"
2. Select your data source (Prometheus)
3. Enter a PromQL query, for example:
   ```promql
   rate(http_requests_total[5m])
   ```
4. Configure visualization settings
5. Click "Apply"

### Example PromQL Queries

```promql
# Request rate per endpoint
sum(rate(http_requests_total[5m])) by (handler)

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# Error rate
(sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100

# Memory growth
delta(process_resident_memory_bytes[1h])

# 99th percentile latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

## 🐛 Troubleshooting

### Dashboard Not Showing Data

1. **Check Prometheus is scraping:**
   ```powershell
   # Visit http://localhost:9090/targets
   # All targets should show "UP" status
   ```

2. **Verify metrics endpoint:**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8000/metrics" -UseBasicParsing
   ```

3. **Generate some traffic:**
   ```powershell
   .\scripts\generate-traffic.ps1
   ```

4. **Check Grafana logs:**
   ```powershell
   docker logs customerllm-grafana --tail 50
   ```

### Prometheus Not Scraping

1. **Check Prometheus configuration:**
   ```powershell
   # View prometheus.yml
   Get-Content infrastructure/monitoring/prometheus.yml
   ```

2. **Restart Prometheus:**
   ```powershell
   docker compose restart prometheus
   ```

### Dashboard JSON Not Loading

1. **Check file location:**
   ```powershell
   Test-Path infrastructure/monitoring/grafana/dashboards/customerllm-dashboard.json
   ```

2. **Check provisioning:**
   ```powershell
   docker logs customerllm-grafana | Select-String "dashboard"
   ```

3. **Restart Grafana:**
   ```powershell
   docker compose restart grafana
   ```

## 📱 Mobile Access

Grafana dashboards work great on mobile devices:

1. Navigate to http://YOUR_SERVER_IP:3001 on your phone
2. Log in with the same credentials
3. Dashboards are responsive and touch-friendly

## 🔒 Security Considerations

### Production Deployment

1. **Change default password:**
   ```yaml
   # In docker-compose.yml
   environment:
     - GF_SECURITY_ADMIN_PASSWORD=your_strong_password
   ```

2. **Enable HTTPS:**
   - Use a reverse proxy (Nginx/Traefik)
   - Configure SSL certificates

3. **Restrict access:**
   - Use firewall rules
   - Implement authentication (OAuth, LDAP)

4. **Regular backups:**
   ```powershell
   # Backup Grafana data
   docker compose exec grafana tar -czf /tmp/grafana-backup.tar.gz /var/lib/grafana
   docker cp customerllm-grafana:/tmp/grafana-backup.tar.gz ./backups/
   ```

## 📚 Additional Resources

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [FastAPI Prometheus Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)

## 🎯 Next Steps

1. **Set up alerting:**
   - Configure alert rules in Grafana
   - Set up notification channels (email, Slack, etc.)

2. **Create custom dashboards:**
   - Business metrics dashboard
   - User activity dashboard
   - Document processing dashboard

3. **Integrate with other services:**
   - Add Qdrant metrics
   - Monitor Ollama performance
   - Track OCR processing times

4. **Set up long-term storage:**
   - Configure Prometheus remote storage
   - Set up data retention policies

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Grafana and Prometheus logs
3. Verify all services are running and healthy
4. Consult the main project documentation

Happy monitoring! 📊

