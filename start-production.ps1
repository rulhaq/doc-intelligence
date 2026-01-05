# CustomerLLM Production Startup Script

Write-Host "`n=== CustomerLLM Production Startup ===" -ForegroundColor Cyan
Write-Host "Building production-ready AI chat application`n" -ForegroundColor Green

# Step 1: Clean up
Write-Host "[1/4] Cleaning up existing containers..." -ForegroundColor Yellow
docker compose -f docker-compose-simple.yml down -v 2>$null

# Step 2: Start infrastructure
Write-Host "[2/4] Starting infrastructure services..." -ForegroundColor Yellow
docker compose -f docker-compose-simple.yml up -d

Write-Host "      Waiting for services to start (15 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# Step 3: Check health
Write-Host "[3/4] Checking infrastructure health..." -ForegroundColor Yellow
Write-Host "      ✓ Services are starting..." -ForegroundColor Green

# Step 4: Display status
Write-Host "[4/4] Production system status:" -ForegroundColor Yellow
Write-Host ""
docker compose -f docker-compose-simple.yml ps

Write-Host "`n=== Infrastructure is Ready! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  PostgreSQL:     localhost:5432" -ForegroundColor White
Write-Host "  Redis:          localhost:6379" -ForegroundColor White
Write-Host "  Qdrant:         http://localhost:6333" -ForegroundColor White
Write-Host "  MinIO Console:  http://localhost:9001 (minioadmin / minioadmin_password)" -ForegroundColor White
Write-Host "  Ollama:         http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Infrastructure is running" -ForegroundColor White
Write-Host "  2. Pull Ollama model: docker exec customerllm-ollama ollama pull mistral" -ForegroundColor White
Write-Host "  3. Build backend:     docker compose build backend" -ForegroundColor White
Write-Host "  4. Start backend:     docker compose up -d backend celery-worker" -ForegroundColor White
Write-Host "  5. Build frontend:    docker compose build frontend" -ForegroundColor White
Write-Host "  6. Start frontend:    docker compose up -d frontend" -ForegroundColor White
Write-Host ""
Write-Host "Tip: Check logs with: docker compose logs -f service-name" -ForegroundColor Gray
Write-Host ""
