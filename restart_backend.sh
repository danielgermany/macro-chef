#!/bin/bash
# Restart Backend Server Script (Linux/Mac)
# This script stops any running backend processes and restarts the server

echo "========================================"
echo "   RESTARTING BACKEND SERVER"
echo "========================================"
echo ""

# Find and stop any running uvicorn processes
echo "Stopping existing backend processes..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null

# Alternative: Kill by port
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Stopping process on port 8000..."
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null
    sleep 2
fi

echo ""
echo "Starting backend server..."
echo ""

# Change to backend directory and start server
cd backend

# Start backend in background
nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &

cd ..

echo ""
echo "Backend server starting..."
echo "Server will be available at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

# Wait a moment and test
sleep 3

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend server is running!"
else
    echo "Backend server may still be starting. Check backend.log for status."
fi

echo ""
echo "========================================"
echo "   BACKEND RESTART COMPLETE"
echo "========================================"
echo ""
