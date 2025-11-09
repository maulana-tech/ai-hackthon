#!/bin/bash

echo "🚀 Starting TrendScout for GetCirclo Testing"
echo "=========================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Installing..."
    brew install ngrok
fi

# Kill existing servers
echo "🔄 Stopping existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -f ngrok 2>/dev/null
sleep 2

# Start the FastAPI server
echo "✅ Starting FastAPI server on port 8000..."
cd "$(dirname "$0")"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/getcirclo_test.log 2>&1 &
SERVER_PID=$!
sleep 5

# Check if server started successfully
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Server is healthy"
else
    echo "❌ Server failed to start. Check logs/getcirclo_test.log"
    exit 1
fi

# Start ngrok tunnel
echo "🌐 Starting ngrok tunnel..."
ngrok http 8000 > logs/ngrok.log 2>&1 &
NGROK_PID=$!
sleep 3

# Get ngrok public URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    echo "Try: ngrok http 8000"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ TrendScout is ready for GetCirclo!"
echo "=========================================="
echo ""
echo "📡 Webhook URL:"
echo "   $NGROK_URL/circlo-webhook/hook"
echo ""
echo "📋 Configure this URL in GetCirclo Dashboard:"
echo "   1. Go to GetCirclo Settings → Webhooks"
echo "   2. Add webhook URL: $NGROK_URL/circlo-webhook/hook"
echo "   3. Method: POST"
echo "   4. Content-Type: application/json"
echo ""
echo "🧪 Test Queries:"
echo "   - 'carikan supplier sepatu sneakers'"
echo "   - 'cari produk tas wanita terlaris'"
echo "   - 'supplier fashion import'"
echo ""
echo "📊 Monitor:"
echo "   - Logs: tail -f logs/getcirclo_test.log"
echo "   - Health: curl $NGROK_URL/health"
echo ""
echo "⚙️  Current Mode: $(cat .env | grep SCRAPING_MODE | cut -d'=' -f2)"
echo ""
echo "🛑 Stop servers:"
echo "   ./stop_services.sh"
echo ""
echo "=========================================="
echo "Press Ctrl+C to stop..."
echo ""

# Keep script running
tail -f logs/getcirclo_test.log
