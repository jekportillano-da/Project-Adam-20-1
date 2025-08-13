# Start all services for Budget Buddy demo
Write-Host "🚀 Starting Budget Buddy Demo Environment" -ForegroundColor Green
Write-Host ""

# Start microservices in background
Write-Host "Starting microservices..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList "-Command", "cd '$PSScriptRoot'; `$env:ENV='dev'; `$env:PORT='8001'; .\.venv\Scripts\python.exe .\services\budget-service\main.py" -WindowStyle Minimized
Start-Sleep 2

Start-Process powershell -ArgumentList "-Command", "cd '$PSScriptRoot'; `$env:ENV='dev'; `$env:PORT='8002'; .\.venv\Scripts\python.exe .\services\savings-service\main.py" -WindowStyle Minimized
Start-Sleep 2

Start-Process powershell -ArgumentList "-Command", "cd '$PSScriptRoot'; `$env:ENV='dev'; `$env:PORT='8003'; .\.venv\Scripts\python.exe .\services\insights-service\main.py" -WindowStyle Minimized
Start-Sleep 2

Write-Host "✅ Budget Service (8001)" -ForegroundColor Green
Write-Host "✅ Savings Service (8002)" -ForegroundColor Green  
Write-Host "✅ Insights Service (8003)" -ForegroundColor Green
Write-Host ""

# Start main gateway server
Write-Host "Starting main gateway server..." -ForegroundColor Yellow
$env:ENV = 'dev'
$env:PORT = '8000'
.\.venv\Scripts\python.exe .\main_dev.py
