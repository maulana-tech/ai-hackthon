#!/bin/bash

echo "🛑 Stopping TrendScout AI services..."
echo ""

# Stop FastAPI server
echo "📦 Stopping FastAPI server..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Server stopped"
else
    echo "ℹ️  Server not running"
fi

# Stop ngrok
echo "🚇 Stopping ngrok tunnel..."
pkill -f ngrok 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Ngrok stopped"
else
    echo "ℹ️  Ngrok not running"
fi

echo ""
echo "✅ All services stopped"
