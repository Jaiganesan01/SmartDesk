Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   SmartDesk AI - Cognitive ITSM Platform Launcher" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1/3] Starting Cognitive Backend on Port 5000..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k cd backend && node server.js" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host "[2/3] Starting Next.js Frontend on Port 3000..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k cd frontend && npm.cmd run dev" -WindowStyle Normal

Start-Sleep -Seconds 4

Write-Host "[3/3] Launching browser to http://localhost:3000..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  SmartDesk AI is now LIVE at http://localhost:3000!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
