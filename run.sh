#!/bin/bash

# TrendScout Supplier Connector - Quick Start Script

echo "🚀 TrendScout Supplier Connector"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✅ .env created! Please edit it with your API keys."
    echo ""
    echo "Required API keys:"
    echo "  - FIRECRAWL_API_KEY (get from https://firecrawl.dev)"
    echo "  - GETCIRCLO_API_KEY"
    echo "  - OPENAI_API_KEY"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  UV package manager not found!"
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies with UV..."
uv pip install -e .

# Create data directories
mkdir -p data/memory
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting TrendScout API Server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""

# Run the app
uv run python app/main.py
