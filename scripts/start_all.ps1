# Quick start script for both servers
Write-Host "Starting Budget Buddy servers..." -ForegroundColor Green

# Kill any existing python processes (optional)
Get-Process | Where-Object { $_.ProcessName -eq 'python' } | Stop-Process -Force -ErrorAction SilentlyContinue

Set-Location "D:/Jek's Projects/Project-Adam-20-1"

# Start microservices in background
$services = @(8001, 8002, 8003)
$serviceNames = @('budget-service', 'savings-service', 'insights-service')

for ($i = 0; $i -lt $services.Length; $i++) {
    $port = $services[$i]
    $name = $serviceNames[$i]
    $svcDir = "services/$name"
    
    Write-Host "Starting $name on port $port"
    Start-Process -WindowStyle Hidden -WorkingDirectory $svcDir -FilePath "python" -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port $port"
}

Start-Sleep -Seconds 3

# Start dev server (demo)
Write-Host "Starting DEV server (demo) on port 8000" -ForegroundColor Cyan
$env:ENV = 'dev'
$env:PORT = '8000'
Start-Process -WindowStyle Hidden -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "main_dev.py"

# Start prod server
Write-Host "Starting PROD server on port 8080" -ForegroundColor Red
$env:ENV = 'prod'
$env:PORT = '8080'
Start-Process -WindowStyle Hidden -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "main_prod.py"

Start-Sleep -Seconds 5

Write-Host "`nServers starting... Check these URLs:" -ForegroundColor Yellow
Write-Host "Demo: http://localhost:8000/demo" -ForegroundColor Cyan
Write-Host "Prod: http://localhost:8080/login" -ForegroundColor Red
Write-Host "API Health: http://localhost:8000/api/health" -ForegroundColor Green
