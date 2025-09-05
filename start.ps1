# start.ps1
Write-Host "Starting all services..."

Start-Process powershell -ArgumentList "-Command", "Write-Host '--- Starting Backend ---'; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-Command", "Write-Host '--- Starting Simulator ---'; python simulator/simulator.py"
Start-Process powershell -ArgumentList "-Command", "Write-Host '--- Starting Dashboard ---'; python -m streamlit run dashboard/dashboard.py"

Write-Host "All services have been launched in separate windows."