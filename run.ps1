# NeonClipping launcher (Windows)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

# 1. Ensure Ollama is running
$env:OLLAMA_IGPU_ENABLE = '1'
try {
    $null = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 -ErrorAction Stop
} catch {
    Write-Host "Ollama background mein start ho raha hai..." -ForegroundColor Cyan
    $ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    if (Test-Path $ollamaExe) {
        Start-Process $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    }
    Start-Sleep -Seconds 2
}

# 2. Check virtual environment
if (-not (Test-Path .venv/Scripts/python.exe)) {
    python -m venv .venv
    .venv/Scripts/python.exe -m pip install -r requirements.txt
}

# 3. Enable Phone Access & Set LAN
$env:NEONCLIPPING_LAN = '1'

# 4. Open Chrome / Default Browser on PC
try { Start-Process 'http://127.0.0.1:8770' } catch {}

# 5. Run NeonClipping
Write-Host "`n===============================================" -ForegroundColor Green
Write-Host " PC URL:    http://127.0.0.1:8770" -ForegroundColor Green
Write-Host " Phone URL: http://192.168.1.9:8770 (same Wi-Fi)" -ForegroundColor Cyan
Write-Host " App band karne ke liye yeh window close karein." -ForegroundColor Yellow
Write-Host "===============================================`n" -ForegroundColor Green
.venv/Scripts/python.exe app.py
