# PowerShell script to run production server
Write-Host "🔒 Starting Production Server (Port 8080)" -ForegroundColor Red
Write-Host "Authentication required for main routes" -ForegroundColor Yellow
Write-Host "Access at: http://localhost:8080/" -ForegroundColor Cyan
Write-Host "Login at: http://localhost:8080/login" -ForegroundColor Cyan
Write-Host "Swagger docs: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host ""

try {
    & python prod_server.py
} catch {
    Write-Host "Error starting production server: $_" -ForegroundColor Red
    Write-Host "Make sure Python and required packages are installed" -ForegroundColor Yellow
}

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
