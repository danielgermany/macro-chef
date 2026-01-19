# Restart Backend Server Script
# This script stops any running backend processes and restarts the server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   RESTARTING BACKEND SERVER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find and stop any running uvicorn processes
Write-Host "Stopping existing backend processes..." -ForegroundColor Yellow

# Kill by port (most reliable method)
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($portProcess) {
    Write-Host "Stopping process on port 8000 (PID: $portProcess)..." -ForegroundColor Yellow
    Stop-Process -Id $portProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "Backend process stopped." -ForegroundColor Green
} else {
    Write-Host "No process found on port 8000." -ForegroundColor Gray
}


Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host ""

# Change to backend directory and start server
Set-Location "$PSScriptRoot\backend"

# Start backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

Write-Host ""
Write-Host "Backend server starting..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Waiting 3 seconds for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test if server is responding
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "Backend server is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "Backend server may still be starting. Check the server window for status." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BACKEND RESTART COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
