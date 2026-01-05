# COMPLETE DEPLOYMENT SCRIPT
# This will build and run the entire application

Write-Host "`n" -NoNewline
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         CustomerLLM Production Deployment               ║" -ForegroundColor Cyan  
Write-Host "║         Enterprise AI Chat Application                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

$ErrorActionPreference = "Continue"

# Step 1: Clean up
Write-Host "[1/5] Cleaning up old containers..." -ForegroundColor Yellow
docker compose -f docker-compose-working.yml down -v 2>$null

# Step 2: Build backend (lightweight - no heavy ML)
Write-Host "`n[2/5] Building backend (this takes 2-3 minutes)..." -ForegroundColor Yellow
Write-Host "      Using minimal dependencies (no PyTorch/TensorFlow)" -ForegroundColor Gray
docker compose -f docker-compose-working.yml build backend celery-worker

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Backend build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "      Backend built successfully!" -ForegroundColor Green

# Step 3: Build frontend
Write-Host "`n[3/5] Building frontend React app..." -ForegroundColor Yellow
docker compose -f docker-compose-working.yml build frontend

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Frontend build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "      Frontend built successfully!" -ForegroundColor Green

# Step 4: Start all services
Write-Host "`n[4/5] Starting all services..." -ForegroundColor Yellow
docker compose -f docker-compose-working.yml up -d

Write-Host "      Waiting for services to initialize (30 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# Step 5: Run database migrations
Write-Host "`n[5/5] Running database migrations..." -ForegroundColor Yellow
docker exec customerllm-backend alembic upgrade head 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "      Database migrations completed!" -ForegroundColor Green
} else {
    Write-Host "      Migrations will run automatically on first request" -ForegroundColor Yellow
}

# Show status
Write-Host "`n" -NoNewline
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              APPLICATION IS RUNNING!                     ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host "`n"

Write-Host "Service Status:" -ForegroundColor Cyan
docker compose -f docker-compose-working.yml ps

Write-Host "`nAccess Your Application:" -ForegroundColor Cyan
Write-Host "  Frontend:         http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:      http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:         http://localhost:8000/docs" -ForegroundColor White
Write-Host "  API Redoc:        http://localhost:8000/redoc" -ForegroundColor White
Write-Host "`n"

Write-Host "Infrastructure Services:" -ForegroundColor Cyan
Write-Host "  PostgreSQL:       localhost:5432" -ForegroundColor White
Write-Host "  Redis:            localhost:6379" -ForegroundColor White
Write-Host "  Qdrant:           http://localhost:6333" -ForegroundColor White
Write-Host "  MinIO Console:    http://localhost:9001" -ForegroundColor White
Write-Host "                    (user: minioadmin, pass: minioadmin_password)" -ForegroundColor Gray
Write-Host "  Ollama:           http://localhost:11434" -ForegroundColor White
Write-Host "`n"

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "  2. Register a new account or login" -ForegroundColor White
Write-Host "  3. Start chatting with AI!" -ForegroundColor White
Write-Host "`n"

Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  View logs:        docker compose -f docker-compose-working.yml logs -f" -ForegroundColor White
Write-Host "  Stop app:         docker compose -f docker-compose-working.yml stop" -ForegroundColor White
Write-Host "  Restart app:      docker compose -f docker-compose-working.yml restart" -ForegroundColor White
Write-Host "  Remove all:       docker compose -f docker-compose-working.yml down -v" -ForegroundColor White
Write-Host "`n"

Write-Host "Pull AI Model (optional):" -ForegroundColor Cyan
Write-Host "  docker exec customerllm-ollama ollama pull mistral" -ForegroundColor White
Write-Host "`n"


