#!/bin/bash

#!/bin/bash

echo "🚀 Starting TrendScout AI with Ngrok + GetCirclo Integration"
echo "=" * 80
echo ""

# Kill existing processes
echo "🔄 Stopping existing services..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -f ngrok 2>/dev/null
sleep 2

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok not found!"
    echo ""
    echo "Install with: brew install ngrok"
    echo "Or download from: https://ngrok.com/download"
    echo ""
    exit 1
fi

echo "✅ Ngrok found"
echo ""

# Start ngrok in background
echo "🚇 Starting ngrok tunnel..."
ngrok http 8000 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 4

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    echo "Check ngrok dashboard: http://127.0.0.1:4040"
    exit 1
fi

echo "✅ Ngrok tunnel active: $NGROK_URL"
echo ""

# Set environment variables
export APP_BASE_URL=$NGROK_URL
export AGENT_WEBHOOK_URL=$NGROK_URL/circlo-webhook/hook

# Start server with ngrok URL
echo "🚀 Starting FastAPI server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 6

# Test health endpoint
HEALTH=$(curl -s $NGROK_URL/health 2>/dev/null)

if [[ $HEALTH == *"healthy"* ]]; then
    echo "✅ Server started successfully"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "                    🎉 SETUP COMPLETE!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 URLS:"
    echo "  🌐 Ngrok Public URL: $NGROK_URL"
    echo "  📊 Ngrok Dashboard:  http://127.0.0.1:4040"
    echo "  🔗 GetCirclo Webhook: $AGENT_WEBHOOK_URL"
    echo "  📄 Test Document:     $NGROK_URL/documents/test/view"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 NEXT STEPS:"
    echo ""
    echo "1️⃣  Register Agent on GetCirclo (One-time):"
    echo "    python3 scripts/register_circlo_agent.py"
    echo ""
    echo "2️⃣  Test in GetCirclo App:"
    echo "    - Search for: @trendscout-ai"
    echo "    - Send: 'Buat kampanye marketing untuk smartwatch'"
    echo "    - Click document URL yang muncul"
    echo ""
    echo "3️⃣  Monitor Activity:"
    echo "    tail -f logs/server.log"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "💡 TIPS:"
    echo "  - Ngrok URL berubah setiap restart (free tier)"
    echo "  - Untuk fixed URL: Upgrade ke Ngrok Pro ($10/month)"
    echo "  - Documents: Beautiful HTML websites dengan automation"
    echo "  - Automation: 5 steps (Review, Budget, Calendar, Tracking, Checklist)"
    echo ""
    echo "🛑 TO STOP:"
    echo "  Press Ctrl+C or run: ./stop_services.sh"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
else
    echo "❌ Server failed to start"
    echo ""
    echo "Check logs: tail -f logs/server.log"
    echo ""
    exit 1
fi

# Keep script running
echo "✅ Services running. Press Ctrl+C to stop..."
echo ""

# Trap Ctrl+C
trap cleanup INT

cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    pkill -f ngrok 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

wait
