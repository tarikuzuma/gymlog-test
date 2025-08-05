Write-Host "Installing Gym Logger Dependencies..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow

# Install pip if not available
python -m ensurepip --upgrade

# Install requirements
pip install -r requirements.txt

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "1. Open PowerShell in this directory" -ForegroundColor White
Write-Host "2. Run: python main.py" -ForegroundColor White
Write-Host "3. Open browser and go to: http://localhost:5001" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit" 