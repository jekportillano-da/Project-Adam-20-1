Environment setup summary for this machine (Windows)

- Python: Installed via winget (3.12)
- Root virtual environment: .venv created and populated from requirements.txt
- Service virtual environments: created under services/*/.venv with their own requirements
- Node.js: Installed via winget (LTS) if not present; open a new terminal to refresh PATH
- VS Code: .vscode/settings.json points to root .venv for default interpreter and pytest

Quick commands (PowerShell):

- Re-run setup script:
  .\scripts\setup.ps1 -InstallNode

- Run demo server:
  .\.venv\Scripts\python.exe main_dev.py

- Run production server:
  .\.venv\Scripts\python.exe main_prod.py

- Run tests:
  .\.venv\Scripts\python.exe -m pytest -q

- Freeze versions:
  .\.venv\Scripts\pip.exe freeze > requirements.lock.txt
