Param(
  [switch]$InstallNode
)

Write-Host "== Project-Adam setup =="
$ErrorActionPreference = 'Continue'

# Ensure Python 3.12
try { $null = & py -3.12 -V 2>$null } catch {}
if (-not $?) {
  $pythonPath = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
  if (-not (Test-Path $pythonPath)) {
    Write-Host "Installing Python 3.12 via winget..."
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent | Out-Null
    Start-Sleep -Seconds 5
  }
}

$pyExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $pyExe)) { throw "Python 3.12 not found. Please install and re-run." }

# Root venv
$root = Get-Location
$venv = Join-Path $root ".venv"
if (-not (Test-Path $venv)) { & $pyExe -m venv $venv }
$rootPy = Join-Path $venv "Scripts/python.exe"
$rootPip = Join-Path $venv "Scripts/pip.exe"
& $rootPy -m pip install --upgrade pip setuptools wheel
& $rootPip install --upgrade -r (Join-Path $root "requirements.txt")

# Services venvs
$servicesDir = Join-Path $root "services"
if (Test-Path $servicesDir) {
  Get-ChildItem -Path $servicesDir -Directory | ForEach-Object {
    $svc = $_.FullName
    $req = Join-Path $svc "requirements.txt"
    if (Test-Path $req) {
      Write-Host "Setting up venv for $($_.Name)"
      $svcVenv = Join-Path $svc ".venv"
      if (-not (Test-Path $svcVenv)) { & $pyExe -m venv $svcVenv }
      $svcPy = Join-Path $svcVenv "Scripts/python.exe"
      $svcPip = Join-Path $svcVenv "Scripts/pip.exe"
      & $svcPy -m pip install --upgrade pip setuptools wheel
      & $svcPip install --upgrade -r $req
    }
  }
}

# Smoke checks
& $rootPy - << 'PY'
import fastapi, httpx, jinja2, openai, pydantic
print('Root OK:', fastapi.__version__, httpx.__version__, jinja2.__version__, openai.__version__, pydantic.__version__)
PY

# Optional Node install
if ($InstallNode) {
  $nodeVersion = & node --version 2>$null
  if (-not $nodeVersion) {
    Write-Host "Installing Node.js LTS via winget..."
    winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements --silent | Out-Null
    Write-Host "Node.js installed. Open a new terminal to pick up PATH changes."
  } else {
    Write-Host "Node present: $nodeVersion"
  }
}

Write-Host "Setup complete."
