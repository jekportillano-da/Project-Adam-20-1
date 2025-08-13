# PowerShell script to run development server
Write-Host "🎭 Starting Development Server (Port 8000)" -ForegroundColor Green
Write-Host "Demo mode - No authentication required" -ForegroundColor Yellow
Write-Host "Access at: http://localhost:8000/demo" -ForegroundColor Cyan
Write-Host "Swagger docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

try {
    $env:ENV = 'dev'
    $env:PORT = '8000'
    if (Test-Path .\.venv\Scripts\python.exe) {
        & .\.venv\Scripts\python.exe .\main_dev.py
    } else {
        & python .\main_dev.py
    }
} catch {
    Write-Host "Error starting development server: $_" -ForegroundColor Red
    Write-Host "Make sure Python and required packages are installed" -ForegroundColor Yellow
}
