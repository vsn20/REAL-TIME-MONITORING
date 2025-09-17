# start.ps1
Write-Host "--- Starting all services for the Real-Time Monitoring System ---"

# Step 1: Start the database in the background
Write-Host "[1/4] Starting TimescaleDB via Docker..."
docker-compose up -d
Write-Host "Database is starting. Waiting 10 seconds for it to initialize..."
Start-Sleep -s 10

# Step 2: Start the FastAPI Backend in a new window
Write-Host "[2/4] Starting FastAPI Backend..."
Start-Process powershell -ArgumentList "-Command", "Write-Host '--- Starting Backend ---'; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

# Step 3: Start the React Dashboard in a new window
Write-Host "[3/4] Starting React Dashboard..."
Start-Process powershell -ArgumentList "-Command", "Write-Host '--- Starting React Dashboard ---'; cd dashboard; npm start"

# Step 4: Start the Simulator in a new window
Write-Host "[4/4] Starting Device Simulator..."
Start-Process powershell -ArgumentList "-Command", "Write-Host '--- Starting Simulator ---'; python simulator/simulator.py"

Write-Host "✅ All services have been launched in separate windows."