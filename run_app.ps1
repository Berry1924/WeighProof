# WeighProof PowerShell Launcher
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Starting WeighProof: OIML R 76 NAWI Test Report Generator (SIH 2026)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

$env:PYTHONPATH = "$PSScriptRoot\backend"
Write-Host "Opening WeighProof Full-Stack App on http://localhost:8000 ..." -ForegroundColor Yellow
python "$PSScriptRoot\backend\main.py"
