# AI Learning System Development Servers
# This script starts both the frontend and backend development servers

Write-Host "Starting AI Learning System Development Environment..." -ForegroundColor Green

# Start backend server in background
Write-Host "Starting Backend Server (Django)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python manage.py runserver 0.0.0.0:8000"

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start frontend server
Write-Host "Starting Frontend Server (React)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host "`nBoth servers are starting up..." -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "`nThe landing page will open automatically in your browser!" -ForegroundColor Magenta
