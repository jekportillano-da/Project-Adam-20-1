# PowerShell script to run development server
Write-Host "🎭 Starting Development Server (Port 8000)" -ForegroundColor Green
Write-Host "Demo mode - No authentication required" -ForegroundColor Yellow
Write-Host "Access at: http://localhost:8000/demo" -ForegroundColor Cyan
Write-Host "Swagger docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

try {
    & python dev_server.py
} catch {
    Write-Host "Error starting development server: $_" -ForegroundColor Red
    Write-Host "Make sure Python and required packages are installed" -ForegroundColor Yellow
}

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
