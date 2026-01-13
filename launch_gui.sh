#!/bin/bash
# Launcher script for Macro Chef GUI

echo " Starting Macro Chef GUI..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo " Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if database exists
if [ ! -f "database/meal_planner.db" ]; then
    echo "  Database not found. Initializing..."
    python3 scripts/db_setup.py
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "  Warning: .env file not found"
    echo "   API features may not work. Copy .env.example to .env and add your API keys."
    echo ""
fi

# Launch GUI
echo " Launching Macro Chef GUI..."
python3 gui_app.py

# If GUI exits with error
if [ $? -ne 0 ]; then
    echo ""
    echo " GUI exited with an error"
    echo "   Check the error message above for details"
    exit 1
fi
