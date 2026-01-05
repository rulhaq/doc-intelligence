# Start CustomerLLM Application
Write-Host "`n=== Starting CustomerLLM Application ===" -ForegroundColor Cyan

# Start infrastructure
Write-Host "`n[1/3] Starting infrastructure..." -ForegroundColor Yellow
docker compose -f docker-compose-simple.yml up -d

Write-Host "Waiting 10 seconds for services to start..."
Start-Sleep -Seconds 10

# Check infrastructure
Write-Host "`n[2/3] Infrastructure status:" -ForegroundColor Yellow
docker compose -f docker-compose-simple.yml ps

Write-Host "`n[3/3] Next steps:" -ForegroundColor Green
Write-Host "  Infrastructure is running!"
Write-Host ""
Write-Host "  To run the backend:" -ForegroundColor White
Write-Host "    cd backend"
Write-Host "    python -m venv venv"
Write-Host "    .\venv\Scripts\activate"
Write-Host "    pip install -r requirements-local.txt"
Write-Host "    python -m uvicorn app.main:app --reload"
Write-Host ""
Write-Host "  To run the frontend:" -ForegroundColor White
Write-Host "    cd frontend"
Write-Host "    npm install"
Write-Host "    npm run dev"
Write-Host ""
Write-Host "See RUN-LOCAL.md for complete instructions" -ForegroundColor Gray
Write-Host ""

