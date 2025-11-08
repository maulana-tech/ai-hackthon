#!/bin/bash

# Quick Deploy Script for Local Testing with ngrok
# This script helps you deploy TrendScout AI to GetCirclo for testing

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "  🚀 TrendScout AI - Local Deployment with ngrok"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if server is running
echo "🔍 Checking if server is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Server is running on port 8000"
else
    echo "❌ Server is NOT running!"
    echo ""
    echo "Please start the server first:"
    echo "  cd /Users/em/web/ai-hackthon"
    echo "  source .venv/bin/activate"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi
echo ""

# Check if ngrok is installed
echo "🔍 Checking if ngrok is installed..."
if command -v ngrok &> /dev/null; then
    echo "✅ ngrok is installed"
else
    echo "❌ ngrok is NOT installed"
    echo ""
    echo "Installing ngrok..."
    if command -v brew &> /dev/null; then
        echo "Using Homebrew to install ngrok..."
        brew install ngrok
        echo "✅ ngrok installed successfully!"
    else
        echo "❌ Homebrew not found"
        echo ""
        echo "Please install ngrok manually:"
        echo "  1. Visit: https://ngrok.com/download"
        echo "  2. Download ngrok for your platform"
        echo "  3. Extract and move to /usr/local/bin/"
        echo "  4. Run this script again"
        echo ""
        exit 1
    fi
fi
echo ""

# Check if ngrok is already running
if pgrep -f "ngrok http" > /dev/null; then
    echo "⚠️  ngrok is already running"
    echo ""
    echo "To get the current URL:"
    echo "  curl -s http://localhost:4040/api/tunnels | python3 -m json.tool"
    echo ""
    echo "Or stop it and restart:"
    echo "  pkill ngrok"
    echo "  ngrok http 8000"
    echo ""
    exit 0
fi

echo "════════════════════════════════════════════════════════════════"
echo "  📡 Starting ngrok tunnel..."
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Starting ngrok in background..."
echo "This will create a public HTTPS URL for your local server."
echo ""

# Start ngrok in background
nohup ngrok http 8000 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

echo "✅ ngrok started (PID: $NGROK_PID)"
echo "⏳ Waiting for ngrok to initialize..."
sleep 3

# Get ngrok URL
echo ""
echo "🔍 Getting ngrok public URL..."

NGROK_URL=""
for i in {1..10}; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else '')" 2>/dev/null || echo "")
    
    if [ -n "$NGROK_URL" ]; then
        break
    fi
    
    echo "  Attempt $i/10..."
    sleep 1
done

if [ -z "$NGROK_URL" ]; then
    echo "❌ Could not get ngrok URL"
    echo ""
    echo "Please check ngrok logs:"
    echo "  cat /tmp/ngrok.log"
    echo ""
    echo "Or manually get the URL:"
    echo "  curl http://localhost:4040/api/tunnels"
    echo ""
    exit 1
fi

echo "✅ ngrok tunnel is ready!"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  🌐 Your Public URL"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  $NGROK_URL"
echo ""
echo "  Webhook: $NGROK_URL/circlo-webhook/hook"
echo ""

# Export webhook URL
export AGENT_WEBHOOK_URL="$NGROK_URL/circlo-webhook/hook"

echo "════════════════════════════════════════════════════════════════"
echo "  🤖 Ready to Register Agent"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Your webhook URL has been set:"
echo "  AGENT_WEBHOOK_URL=$AGENT_WEBHOOK_URL"
echo ""
echo "Next steps:"
echo ""
echo "1. Test webhook endpoint:"
echo "   curl $NGROK_URL/circlo-webhook/webhook-info"
echo ""
echo "2. Register agent on GetCirclo:"
echo "   export AGENT_WEBHOOK_URL=\"$AGENT_WEBHOOK_URL\""
echo "   python scripts/register_circlo_agent.py"
echo ""
echo "3. Test in GetCirclo app:"
echo "   - Search for: @trendscout-ai"
echo "   - Send: Carikan produk elektronik terlaris"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  📊 Monitoring"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Watch logs:"
echo "  tail -f logs/server.log"
echo ""
echo "Watch ngrok traffic:"
echo "  Open in browser: http://localhost:4040"
echo ""
echo "Stop ngrok:"
echo "  kill $NGROK_PID"
echo "  # or: pkill ngrok"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🎉 Your agent is ready to be registered!"
echo ""
