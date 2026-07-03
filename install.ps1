$ErrorActionPreference = "Stop"

Write-Host "Building padam-cli binary..."

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Error: uv is not installed." -ForegroundColor Red
    exit 1
}

uv sync
uv run pyinstaller --onefile --name padam-cli main.py

$installDir = "$env:LOCALAPPDATA\Programs\padam-cli"

New-Item -ItemType Directory -Force -Path $installDir | Out-Null

Copy-Item "dist\padam-cli.exe" "$installDir\padam-cli.exe" -Force

Write-Host "Installed to $installDir" -ForegroundColor Green
Write-Host ""
Write-Host "Add this directory to your PATH:"
Write-Host $installDir