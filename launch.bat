@echo off
title SmartDesk AI Launcher
echo ========================================================
echo    SmartDesk AI - Cognitive ITSM Platform Launcher
echo ========================================================
echo.
echo [1] Launching Cognitive Backend Server on port 5000...
start "SmartDesk AI Backend (Port 5000)" cmd /k "cd backend && node server.js"

timeout /t 2 >nul

echo [2] Launching Enterprise Next.js Frontend on port 3000...
start "SmartDesk AI Next.js Frontend (Port 3000)" cmd /k "cd frontend && npm.cmd run dev"

echo [3] Waiting for servers to initialize...
timeout /t 4 >nul

echo [4] Opening SmartDesk AI in your default browser...
start http://localhost:3000

echo.
echo ========================================================
echo   SmartDesk AI is now LIVE!
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:5000
echo ========================================================
echo.
echo Press any key to also launch the local Streamlit console, or close this window.
pause >nul

start "SmartDesk AI Streamlit Workbench" cmd /k "streamlit run app.py"
