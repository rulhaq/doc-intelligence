# Generate Traffic for Metrics Testing
# This script generates realistic traffic to populate Grafana dashboards

Write-Host "`n=== Generating Test Traffic ===" -ForegroundColor Cyan
Write-Host "This will make API calls to populate metrics in Grafana" -ForegroundColor Yellow

$baseUrl = "http://localhost:8000"
$totalRequests = 0

# Function to make a request
function Make-Request {
    param($endpoint, $method = "GET")
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl$endpoint" -Method $method -UseBasicParsing -TimeoutSec 5
        $script:totalRequests++
        return $true
    } catch {
        $script:totalRequests++
        return $false
    }
}

Write-Host "`nGenerating traffic..." -ForegroundColor Green

# Health check requests (fast)
Write-Host "  [1/5] Health checks..." -NoNewline
for ($i=0; $i -lt 20; $i++) {
    Make-Request "/health" | Out-Null
    Start-Sleep -Milliseconds 100
}
Write-Host " Done (20 requests)" -ForegroundColor Green

# Metrics requests
Write-Host "  [2/5] Metrics endpoint..." -NoNewline
for ($i=0; $i -lt 10; $i++) {
    Make-Request "/metrics" | Out-Null
    Start-Sleep -Milliseconds 200
}
Write-Host " Done (10 requests)" -ForegroundColor Green

# API endpoints (requires auth - will generate 401s which is fine for testing)
Write-Host "  [3/5] API endpoints..." -NoNewline
$endpoints = @("/api/v1/conversations", "/api/v1/admin/documents", "/docs", "/redoc")
foreach ($endpoint in $endpoints) {
    for ($i=0; $i -lt 5; $i++) {
        Make-Request $endpoint | Out-Null
        Start-Sleep -Milliseconds 150
    }
}
Write-Host " Done (20 requests)" -ForegroundColor Green

# Mixed requests
Write-Host "  [4/5] Mixed traffic..." -NoNewline
for ($i=0; $i -lt 15; $i++) {
    $random = Get-Random -Minimum 0 -Maximum 4
    switch ($random) {
        0 { Make-Request "/health" | Out-Null }
        1 { Make-Request "/metrics" | Out-Null }
        2 { Make-Request "/docs" | Out-Null }
        3 { Make-Request "/api/v1/conversations" | Out-Null }
    }
    Start-Sleep -Milliseconds 200
}
Write-Host " Done (15 requests)" -ForegroundColor Green

# Final health check burst
Write-Host "  [5/5] Final burst..." -NoNewline
for ($i=0; $i -lt 10; $i++) {
    Make-Request "/health" | Out-Null
    Start-Sleep -Milliseconds 50
}
Write-Host " Done (10 requests)" -ForegroundColor Green

Write-Host "`n=== Traffic Generation Complete ===" -ForegroundColor Cyan
Write-Host "Total requests made: $totalRequests" -ForegroundColor White
Write-Host "`nMetrics should now be visible in Grafana:" -ForegroundColor Yellow
Write-Host "  URL: http://localhost:3001" -ForegroundColor White
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin" -ForegroundColor White
Write-Host "  Dashboard: CustomerLLM - Application Monitoring" -ForegroundColor White
Write-Host "`nPrometheus metrics can be viewed at:" -ForegroundColor Yellow
Write-Host "  URL: http://localhost:9090" -ForegroundColor White
Write-Host ""

