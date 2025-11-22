#!/bin/bash
set -e

# Navigate to app directory
cd "$(dirname "$0")"

# Kill any existing instance
pkill -f 'python app.py' || true
sleep 1

# Start the app in background
nohup python app.py > app.log 2>&1 &
PID=$!

# Save PID
echo $PID > app.pid
echo "Started Flask app with PID: $PID"

# Wait a moment and verify it's still running
sleep 2
if kill -0 $PID 2>/dev/null; then
    echo "App is running successfully!"
    exit 0
else
    echo "App failed to start. Check app.log for details."
    exit 1
fi